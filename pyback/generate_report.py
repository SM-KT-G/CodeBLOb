import typer
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from typing_extensions import Annotated

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
    )]
):
    """지정된 디렉터리의 파일을 확장자별로 정리합니다."""
    typer.secho(f"Scanning directory: {source_dir}", fg=typer.colors.GREEN)

    try:
        for file_path in source_dir.iterdir():
            # 파일이 아니거나, 이 스크립트 자신이면 건너뛰기
            if not file_path.is_file() or file_path.name == "organize.py":
                continue
            
            category = get_category(file_path)
            
            if category:
                target_category_dir = source_dir / category
                target_file_path = target_category_dir / file_path.name

                try:
                    # 대상 디렉터리 생성 (존재하지 않을 경우)
                    target_category_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 파일 이동
                    shutil.move(str(file_path), str(target_file_path))
                    typer.echo(f"Moved: {file_path.name} -> {target_category_dir.name}/")
                
                except (shutil.Error, OSError) as e:
                    typer.secho(f"Error moving {file_path.name}: {e}", fg=typer.colors.RED, err=True)
            
            else:
                typer.echo(f"Skipped: {file_path.name} (분류 카테고리 없음)")


    except FileNotFoundError:
        typer.secho(f"오류: 소스 디렉터리 '{source_dir}'를 찾을 수 없습니다.", fg=typer.colors.RED, err=True)
    except PermissionError:
        typer.secho(f"오류: '{source_dir}' 디렉터리에 접근 권한이 없습니다.", fg=typer.colors.RED, err=True)
    except Exception as e:
        typer.secho(f"예상치 못한 오류 발생: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
