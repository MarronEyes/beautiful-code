# Dev started at 26/10/2021
if __name__ == "__main__":
    import bottle as bt
    import src.server

    # TODO: get host and port from command-line arguments using argparser
    host = "localhost" if __debug__ else "0.0.0.0"
    port = 8080 if __debug__ else 80
    bt.run(host=host, port=port)
