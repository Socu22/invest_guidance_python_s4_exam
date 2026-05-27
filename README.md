# invest_guidance_python_s4_exam

[Setup .venv]:
    py -3.12 -m venv .venv
    .venv\Scripts\activate        # Windows
    source .venv/bin/activate    # Linux/macOS 
    python -m pip install --upgrade pip
    uv init 
    uv pip install -e .
    pip install requiremnts.txt  - download requirements 
    inside pyproject.toml:
        [tool.setuptools.packages.find]
        where = ["src"]

[Docker]
    docker compose up --build
        put your api keys inside the docker-compose.yml
    docker down

[Setup .env]:
    follow .example.quick.env or .example.custom.env or .example.docker.env
        Make copy at root rename to .env
            login/signup to get/create your API key/key's.  
                API_TOKEN = https://eodhd.com/cp/dashboard
                MISTRAL_API_KEY = https://admin.mistral.ai/organization/api-keys
        


Quick Start: Only put your API key's in. 
    [Client]:
    cd client
    streamlit run app.py (streamlit run client/app.py)
    [Server]:
    cd server
    uvicorn app:app --reload (uvicorn server.app:app --reload)

Custom Start: API key' & insert your prefered ports.
    [Client]:
    cd client
    streamlit run app.py --server.port 8501  (streamlit run client/app.py --server.port 8501)
    [Server]:
    cd server
    uvicorn app:app --reload --port 8000  (uvicorn server.app:app --reload --port 8000)


Dev: Here are some dev tools to use, in case you want to change the code.
    [debug]: 
    ruff check -w   # live  
    ruff check --fix  # fixes
    pyright -w      # live 
    [test]:
    pytest .