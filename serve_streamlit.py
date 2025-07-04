import shlex
import subprocess
from pathlib import Path

import modal

streamlit_script_local_path = Path(__file__).parent / "app.py"
streamlit_script_remote_path = "/root/app.py"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .poetry_install_from_file(poetry_pyproject_toml="pyproject.toml")
    .add_local_file(
        streamlit_script_local_path,
        streamlit_script_remote_path,
    )
)

app = modal.App(name="venmo-splitter", image=image)

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "app.py not found! Place the script with your streamlit app in the same directory."
    )


@app.function()
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    target = shlex.quote(streamlit_script_remote_path)
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)
