def comNDel():
    import os
    import subprocess
    path = os.path.join("debug", "f%08d.png")
    subprocess.call(f"ffmpeg -framerate 100 -i {path} -vcodec libx264 -pix_fmt yuv420p demo.mp4 -y",shell=True)

    import os
    for f in os.listdir('debug'): os.remove(os.path.join('debug', f))


if __name__ == "__main__":
    comNDel()