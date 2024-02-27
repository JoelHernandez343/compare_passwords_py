# Joel Hernández @ 2023

import json
import pandas as pd

from pathlib import Path
from io import TextIOWrapper


def read_bitwarden_json() -> dict:
    path = None

    for file in Path(".").glob("bitwarden*.json"):
        path = file
        break

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    return data


def get_bitwarden_folders(data: dict) -> list[str]:
    folders = [
        f
        for f in data["folders"]
        if f["name"].startswith("_") or f["name"] == "ocdtech_job"
    ]
    folders = [{"id": f["id"], "name": f["name"].strip("_")} for f in folders]

    return folders


def search_for_name(id: str, folders: list[dict]) -> str:
    for folder in folders:
        if folder["id"] == id:
            return f"_{folder['name']}"

    return ""


def get_passwords_from_json() -> list[dict]:
    data = read_bitwarden_json()

    folders = get_bitwarden_folders(data)

    items = data["items"]
    credentials = [
        {
            "name": f"{i['name'].lower().replace(' ', '_')}{search_for_name(i['folderId'], folders)}",
            "username": i["login"]["username"],
            "password": i["login"]["password"],
            "fields": [
                {
                    "name": field["name"],
                    "value": field["value"],
                }
                for field in i.get("fields", [])
            ],
        }
        for i in items
    ]

    return credentials


def read_credential_from_txt(file: TextIOWrapper, name: str) -> dict:
    credential = {
        "name": name.rstrip(":").lower().replace(" ", "_"),
        "fields": [],
    }
    for i, line in enumerate(file):
        line = line.rstrip("\n").strip()

        if not line:
            break

        if i == 0:
            credential["username"] = line
        elif i == 1:
            credential["password"] = line
        elif i > 1:
            credential["fields"].append(line)

        i += 1

    return credential


def get_passwords_from_txt() -> list[dict]:
    credentials = []

    with Path("passwords.txt").open(encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\n")

            if not line:
                continue

            credentials.append(read_credential_from_txt(f, line))

    return credentials


def compare_data(b_data: list[dict], t_data: list[dict]) -> None:
    b_df = pd.DataFrame(b_data).drop(columns=["fields"])
    t_df = pd.DataFrame(t_data).drop(columns=["fields"])

    diff = pd.merge(
        left=b_df,
        right=t_df,
        on=["name", "username", "password"],
        how="outer",
        indicator=True,
    )

    diff = diff[diff["_merge"] != "both"]

    diff.to_excel("diff.xlsx", index=False)


def get_bitwarden_repeated_passwords(data: list[dict]) -> list[dict]:
    passwords = {}

    for item in data:
        p = item["password"]

        if p in passwords:
            passwords[p]["count"] += 1
            passwords[p]["items"].append(item)
        else:
            passwords[p] = {"count": 1, "items": [item]}

    repeated = [j for i in passwords.values() for j in i["items"] if i["count"] > 1]
    pd.DataFrame(repeated).to_excel("repeated_passwords.xlsx", index=False)


def main() -> None:
    bitwarden_credentials = get_passwords_from_json()
    txt_credentials = get_passwords_from_txt()

    # compare_data(bitwarden_credentials, txt_credentials)
    get_bitwarden_repeated_passwords(bitwarden_credentials)


if __name__ == "__main__":
    main()
