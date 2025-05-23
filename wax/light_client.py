from light_module import*



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 client.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    send_command(command)
