# invest_guidance_python_s4_exam

[Setup .venv]:
py -3.14 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate    # Linux/macOS 
uv init 
python -m pip install --upgrade pip
uv pip install -r requirements.txt
uv pip install -e .
inside pyproject.toml:
    [tool.setuptools.packages.find]
    where = ["src"]


[Download requiremnts]:
pip install requiremnts.txt


Start: 
    [Client]:
    cd client
    streamlit run app.py --server.port 8502  (streamlit run client/app.py --server.port 8502)
    [Server]:
    cd server
    uvicorn app:app --reload --port 8080  ([NOT_SUPPORTED]uvicorn server.app:app --reload --port 8080)

Dev: 
    [debug]: 
    ruff check -w  # live
    ruff check --fix
    pyright -w # live 
    [test]:
    pytest .