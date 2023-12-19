import typer

from dotenv import load_dotenv

import ui


app = typer.Typer()


@app.command()
def frontend():
    ui.run()


if __name__ == "__main__":
    load_dotenv()
    app()
