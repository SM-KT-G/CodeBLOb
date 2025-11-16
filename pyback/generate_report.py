import typer
from pathlib import Path
from typing_extensions import Annotated

# Typer 앱 인스턴스 생성
app = typer.Typer(help="파일을 확장자별로 하위 폴더에 정리합니다.")

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
            
            typer.echo(f"Found file: {file_path.name}")

    except FileNotFoundError:
        typer.secho(f"오류: 소스 디렉터리 '{source_dir}'를 찾을 수 없습니다.", fg=typer.colors.RED, err=True)
    except PermissionError:
        typer.secho(f"오류: '{source_dir}' 디렉터리에 접근 권한이 없습니다.", fg=typer.colors.RED, err=True)
    except Exception as e:
        typer.secho(f"예상치 못한 오류 발생: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
