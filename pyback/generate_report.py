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
    typer.secho(f"Target directory to organize: {source_dir}", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
