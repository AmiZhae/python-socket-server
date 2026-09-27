import os
import socket
from datetime import datetime


class SocketServer:
    def __init__(self):
        self.bufsize = 1024

        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()

        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def run(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)

        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)

                print("Request message...\r\n")

                response = b""

                while True:
                    try:
                        data = clnt_sock.recv(self.bufsize)

                        if not data:
                            break

                        response += data

                    except socket.timeout:
                        break

                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

                bin_file = os.path.join(
                    self.DIR_PATH,
                    timestamp + ".bin"
                )

                with open(bin_file, "wb") as file:
                    file.write(response)

                print("Request saved:", bin_file)

                try:
                    header, body = response.split(b"\r\n\r\n", 1)

                    content_type = b"boundary="

                    if content_type in header:
                        boundary = header.split(content_type)[1].split(b"\r\n")[0]
                        boundary = boundary.strip(b'"')

                        parts = body.split(b"--" + boundary)

                        for part in parts:
                            if b'name="image"' in part and b'filename="' in part:

                                part_header, image_data = part.split(
                                    b"\r\n\r\n",
                                    1
                                )

                                filename = part_header.split(
                                    b'filename="'
                                )[1].split(b'"')[0]

                                filename = filename.decode(
                                    "utf-8",
                                    errors="ignore"
                                )

                                extension = os.path.splitext(filename)[1]

                                if not extension:
                                    extension = ".jpg"

                                if image_data.endswith(b"\r\n"):
                                    image_data = image_data[:-2]

                                image_file = os.path.join(
                                    self.DIR_PATH,
                                    timestamp + extension
                                )

                                with open(image_file, "wb") as file:
                                    file.write(image_data)

                                print("Image saved:", image_file)

                                break

                except Exception as e:
                    print("Image save error:", e)

                clnt_sock.sendall(self.RESPONSE)
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")

        self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)