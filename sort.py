from pathlib import Path
import sys
import re
import shutil

images = []
video = []
documents = []
audio = []
archives = []
other = []

FILES_EXTENSIONS_MAP = {
    "JPEG": images,
    "PNG": images,
    "JPG": images,
    "SVG": images,
    "AVI": video,
    "MP4": video,
    "MOV": video,
    "MKV": video,
    "DOC": documents,
    "DOCX": documents,
    "TXT": documents,
    "PDF": documents,
    "XLSX": documents,
    "PPTX": documents,
    "MP3": audio,
    "OGG": audio,
    "WAV": audio,
    "AMR": audio,
    "ZIP": archives,
    "GZ": archives,
    "TAR": archives,
}

FOLDERS_IGNORE = {"picture", "video", "documents", "music", "archives", "other"}
folders = []
extension = set()
other_extension = set()

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a",
    "b",
    "v",
    "g",
    "d",
    "e",
    "e",
    "j",
    "z",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "h",
    "ts",
    "ch",
    "sh",
    "sch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
    "je",
    "i",
    "ji",
    "g",
)

TRANS = {}


def create_trans():
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()


def normalize(file_name):
    new_file_name = file_name.translate(TRANS)
    new_file_name = re.sub(r"(?!\.)\W", "_", new_file_name)
    return new_file_name


def scan(path):
    p = Path(path)
    for file in p.iterdir():
        if file.is_dir():
            if file.name in FOLDERS_IGNORE:
                continue
            folders.append(file)
            scan(file)
        else:
            ext = file.suffix.upper()[1::]
            if FILES_EXTENSIONS_MAP.get(ext) != None:
                FILES_EXTENSIONS_MAP[ext].append(file)
                extension.add(ext)
            else:
                other.append(file)
                other_extension.add(ext)


def move_images_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.move(file, directory / normalize(file.name))


def move_video_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.move(file, directory / normalize(file.name))


def move_documents_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.move(file, directory / normalize(file.name))


def move_audio_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.move(file, directory / normalize(file.name))


def move_archives_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        derectory_for_file = directory / normalize(file.name.replace(file.suffix, ""))
        derectory_for_file.mkdir(exist_ok=True, parents=True)
        try:
            shutil.unpack_archive(file, derectory_for_file)
            file.unlink()
        except shutil.ReadError:
            print("It is not archive")
            derectory_for_file.rmdir()


def move_other_files(files, directory):
    directory.mkdir(exist_ok=True, parents=True)
    for file in files:
        shutil.move(file, directory / normalize(file.name))


def remove_folders(folders):
    for folder in folders:
        try:
            folder.rmdir()
        except OSError:
            print(f"Can't delete folder: {folder}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Path don't enter")
        exit

    p = Path(sys.argv[1])
    if not p.exists():
        print("Path not found")
        exit

    if not p.is_dir():
        print("You must enter path")
        exit

    # create new tranlate dictionary
    create_trans()

    # scan folders
    scan(p)

    # move files
    move_images_files(images, p / "images")
    move_video_files(video, p / "video")
    move_documents_files(documents, p / "documents")
    move_audio_files(audio, p / "audio")
    move_archives_files(archives, p / "archives")
    move_other_files(other, p / "other")

    # remove folders
    remove_folders(folders)

    print("Done")
