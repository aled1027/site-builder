"""
Deletes posts.db:db table and then recreates it from the files in the posts directory.
"""

import glob
from typing import Any

import click
from sqlite_utils import Database
from sqlite_utils.utils import TypeTracker

from .markdown import Markdown


def build_db_from_directory(directory: str, database: str) -> None:
    filenames = glob.glob(f"{directory}/*.md")

    posts: list[dict[str, Any]] = []
    for i, filename in enumerate(filenames):
        try:
            with open(filename) as fh:
                contents = fh.read()
                post = Markdown(filename, contents)
                posts.append(post.as_record())
        except Exception as e:
            print(f"Error building post: {filename}")
            raise e

    posts = sorted(posts, key=lambda p: (p["date"], p["title"]))
    for i, post in enumerate(posts):
        post["id"] = i

    # Next, we're going to build an M2M with a tags table and a posts_tags tables.
    tags_set: set[str] = set()
    for post in posts:
        for tag in post["metadata"]["tags"]:
            tags_set.add(tag)
    tags = list(tags_set)

    tag_records: list[dict[str, Any]] = []
    tag_dict = {}
    for i, tag in enumerate(sorted(tags)):
        tag_records.append({"id": i, "tag": tag})
        tag_dict[tag] = i

    posts_tags_records: list[dict[str, Any]] = []
    for post in posts:
        for tag in post["metadata"]["tags"]:
            posts_tags_records.append(
                {
                    "tag_id": tag_dict[tag],
                    "post_id": post["id"],
                    "id": len(posts_tags_records),
                }
            )

    db = Database(database)
    db["posts"].insert_all(TypeTracker().wrap(posts), pk="id")
    db["posts"].enable_fts(["title", "html_body"])
    db["tags"].insert_all(tag_records, pk="id")
    db["posts_tags"].insert_all(posts_tags_records, pk="id")
    db["posts_tags"].add_foreign_key("post_id", "posts", "id")
    db["posts_tags"].add_foreign_key("tag_id", "tags", "id")


@click.command()
@click.argument("files_dir")
@click.argument("database")
def cli(files_dir: str, database: str) -> None:
    build_db_from_directory(files_dir, database)


if __name__ == "__main__":
    cli()
