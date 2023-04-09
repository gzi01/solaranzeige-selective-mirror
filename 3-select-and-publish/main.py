#!/usr/bin/python3
# Quellcode aus expandiertem Image lesen und in neues Github Repo einchecken
import json
import os
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PathResolved:
    path_to_local_file: Path
    path_in_image: Path


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        dest="imagepath",
        help="Absoluter Pfad zum Solaranzeige.img File.",
        required=True,
    )

    return parser.parse_args(sys.argv[1:])


def load_config(configfile: Optional[Path] = None) -> List[str]:
    if not configfile:
        configfile = Path(__file__).parent.absolute() / Path("relevant_files.json")

    with open(configfile, "r") as fp:
        return json.load(fp)


def resolve_paths_relative_to_image_location(
    image_location: Path, relevant_files: List[str]
) -> List[PathResolved]:
    new_paths = []
    for path in relevant_files:
        new_paths.append(
            PathResolved(
                path_to_local_file=image_location / path[1:],
                path_in_image=Path(path[1:]),
            )
        )

    return new_paths


def unpack_image(imagepath: str) -> Path:
    tempfolder = Path(__file__).parent / "tmp"
    
    # create folder if necessary
    os.makedirs(tempfolder, exist_ok=True)
    # delete in case files of old run are still there
    shutil.rmtree(tempfolder)
    # create tempfolder
    os.mkdir(tempfolder)

    # unpack image
    os.system(f"7z x {imagepath} -o{tempfolder}")
    # unpack root partition (hardcode image name. could also detect image by filesize)
    partition1_path = tempfolder / "1.img"
    os.system(f"7z x {partition1_path} -o{tempfolder}")

    image_root_path = Path(tempfolder)
    return image_root_path


def create_new_image_repository(name: str, resolved_paths: List[PathResolved]):
    path_to_new_repo = Path(__file__).parent.parent.parent / name
    path_to_new_repo.mkdir()

    for path in resolved_paths:
        os.makedirs(str(path_to_new_repo / path.path_in_image.parent), exist_ok=True)
        shutil.copy(path.path_to_local_file, path_to_new_repo / path.path_in_image)



def main():
    args = parse_arguments()
    imagepath = args.imagepath
    image_root_path = unpack_image(imagepath)

    relevant_files = load_config()

    # Gehe davon aus, dass die Pfade im json file absolute Pfade im Image sind
    resolved_paths = resolve_paths_relative_to_image_location(
        image_root_path, relevant_files
    )
    # get name of image without extension
    image_name = os.path.split(os.path.splitext(imagepath)[0])[1]
    create_new_image_repository(image_name, resolved_paths)

    # delete files from unpacking the image
    tempfolder = Path(__file__).parent / "tmp"
    shutil.rmtree(tempfolder)


if __name__ == "__main__":
    main()
