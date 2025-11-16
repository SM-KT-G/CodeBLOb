import typer
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from typing_extensions import Annotated

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 분류 카테고리
CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".svg"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Documents": [".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".txt", ".md"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".go", ".rs"],
}

# Typer 앱 인스턴스 생성
app = typer.Typer(help="파일을 확장자별로 하위 폴더에 정리합니다.")

def get_category(file_path: Path) -> Optional[str]:
    """파일 확장자를 기반으로 카테고리 이름을 반환합니다."""
    ext = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return None

@app.command()
def run(
    source_dir: Annotated[Path, typer.Argument(
        exists=True, 
        file_okay=False, 
        dir_okay=True, 
        readable=True, 
        resolve_path=True,
        help="정리할 파일이 있는 소스 디렉터리"
    )],
    
    dest_dir: Annotated[Optional[Path], typer.Option(
        "--dest", "-d",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="정리된 파일이 저장될 대상 디렉터리 (기본값: 소스 디렉터리)"
    )] = None,
    
    dry_run: Annotated[bool, typer.Option(
        "--dry-run",
        help="실제로 파일을 옮기지 않고 실행 결과만 시뮬레이션합니다."
    )] = False
):
    """지정된 디렉터리의 파일을 확장자별로 정리합니다."""
    
    if dest_dir is None:
        dest_dir = source_dir

    if dry_run:
        logging.info("--- [DRY RUN] ---")
        logging.info(f"소스 디렉터리: {source_dir}")
        logging.info(f"대상 디렉터리: {dest_dir}")
        logging.info("실제 파일 이동은 수행되지 않습니다.")
        typer.echo("--- [DRY RUN] ---")
    else:
        logging.info(f"Scanning directory: {source_dir}")

    processed_files = 0
    skipped_files = 0

    try:
        for file_path in source_dir.iterdir():
            # 파일이 아니거나, 이 스크립트 자신이면 건너뛰기
            if not file_path.is_file() or file_path.name == "organize.py":
                continue
            
            category = get_category(file_path)
            
            if category:
                target_category_dir = dest_dir / category
                target_file_path = target_category_dir / file_path.name

                logging.info(f"Moving: {file_path.name} -> {target_category_dir.name}/")

                if not dry_run:
                    try:
                        # 대상 디렉터리 생성 (존재하지 않을 경우)
                        target_category_dir.mkdir(parents=True, exist_ok=True)
                        
                        # 파일 이동
                        shutil.move(str(file_path), str(target_file_path))
                        processed_files += 1
                    
                    except (shutil.Error, OSError) as e:
                        logging.error(f"Error moving {file_path.name}: {e}")
                        skipped_files += 1
                
                else:
                    # Dry run 모드에서는 처리된 것으로 간주
                    processed_files += 1
            
            else:
                logging.warning(f"Skipped: {file_path.name} (분류 카테고리 없음)")
                skipped_files += 1

        # --- 최종 요약 ---
        summary_color = typer.colors.GREEN if not dry_run else typer.colors.YELLOW
        typer.secho("\n--- 정리 완료 ---", fg=summary_color, bold=True)
        typer.secho(f"총 이동된 파일: {processed_files}", fg=summary_color)
        typer.secho(f"총 건너뛴 파일: {skipped_files}", fg=summary_color)
        if dry_run:
            typer.secho("[DRY RUN 모드로 실행되었습니다]", fg=typer.colors.YELLOW)

    except FileNotFoundError:
        typer.secho(f"오류: 소스 디렉터리 '{source_dir}'를 찾을 수 없습니다.", fg=typer.colors.RED, err=True)
    except PermissionError:
        typer.secho(f"오류: '{source_dir}' 디렉터리에 접근 권한이 없습니다.", fg=typer.colors.RED, err=True)
    except Exception as e:
        typer.secho(f"예상치 못한 오류 발생: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
