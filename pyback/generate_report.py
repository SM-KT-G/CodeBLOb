import typer

# Typer 앱 인스턴스 생성
app = typer.Typer(help="파일을 확장자별로 하위 폴더에 정리합니다.")

@app.command()
def run():
    """지정된 디렉터리의 파일을 확장자별로 정리합니다."""
    typer.echo("File organizer CLI initialized.")

if __name__ == "__main__":
    app()
