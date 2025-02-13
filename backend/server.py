from config import parse_config, ServerConfig
from controller import app

if __name__ == "__main__":
    config: ServerConfig = parse_config()
    print(f"Server Config:\n{config.model_dump_json(indent=4)}")

    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)
