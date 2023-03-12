import datetime

from site_builder.markdown import Markdown


def test_one():
    filename = "foo.md"
    contents = """---
    title: foobar
    date: 1987-02-23
    tags: ['test', "tag"]
    ---

    # Hi 
    
    I'm markdown
    """
    mkd = Markdown(filename, contents)
    assert mkd.metadata.filename == "foo.md"
    assert mkd.metadata.title == "foobar"
    assert mkd.metadata.date == datetime.date(1987, 2, 23)
    assert mkd.metadata.draft is False
    assert mkd.metadata.tags == ["test", "tag"]

    # Check length instead of checking contents
    assert len(mkd.contents) > 10
    assert len(mkd.md_body) > 10
    assert len(mkd.html_body) > 10
    assert len(mkd.html_preview) > 10

    # Check conversion to dictionary
    record = mkd.as_record()
    expected_keys = [
        "title",
        "date",
        "pretty_date",
        "raw_contents",
        "body",
        "html_body",
        "html_preview",
        "metadata",
    ]
    for key in expected_keys:
        assert key in record
