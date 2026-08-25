
from types import SimpleNamespace

from app.sources import notion


def test_extract_rich_text_joins_plain_text() -> None:
    rich_text = [
        {"plain_text": "Hola "},
        {"plain_text": "mundo"},
    ]

    result = notion.extract_rich_text(rich_text)

    assert result == "Hola mundo"


def test_extract_block_text_returns_rich_text() -> None:
    block = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"plain_text": "Texto de prueba"}
            ]
        },
    }

    result = notion.extract_block_text(block)

    assert result == "Texto de prueba"


def test_extract_block_text_returns_empty_string_when_no_rich_text() -> None:
    block = {
        "type": "divider",
        "divider": {},
    }

    result = notion.extract_block_text(block)

    assert result == ""


def test_get_block_children_handles_pagination(monkeypatch) -> None:
    calls = []

    def fake_list(block_id: str, start_cursor=None):
        calls.append(start_cursor)

        if start_cursor is None:
            return {
                "results": [
                    {"id": "block-1"},
                    {"id": "block-2"},
                ],
                "has_more": True,
                "next_cursor": "cursor-2",
            }

        return {
            "results": [
                {"id": "block-3"},
            ],
            "has_more": False,
            "next_cursor": None,
        }

    fake_client = SimpleNamespace(
        blocks=SimpleNamespace(
            children=SimpleNamespace(
                list=fake_list,
            )
        )
    )

    monkeypatch.setattr(
        notion,
        "client",
        fake_client,
    )

    result = notion.get_block_children("page-1")

    assert result == [
        {"id": "block-1"},
        {"id": "block-2"},
        {"id": "block-3"},
    ]

    assert calls == [None, "cursor-2"]


def test_extract_blocks_recursive_includes_nested_blocks(monkeypatch) -> None:
    blocks_by_id = {
        "page-1": [
            {
                "id": "block-1",
                "type": "paragraph",
                "has_children": False,
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Texto principal"}
                    ]
                },
            },
            {
                "id": "block-2",
                "type": "bulleted_list_item",
                "has_children": True,
                "bulleted_list_item": {
                    "rich_text": [
                        {"plain_text": "Elemento padre"}
                    ]
                },
            },
        ],
        "block-2": [
            {
                "id": "block-3",
                "type": "paragraph",
                "has_children": False,
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Texto anidado"}
                    ]
                },
            }
        ],
    }

    monkeypatch.setattr(
        notion,
        "get_block_children",
        lambda block_id: blocks_by_id[block_id],
    )

    result = notion.extract_blocks_recursive("page-1")

    assert result == [
        "Texto principal",
        "Elemento padre",
        "Texto anidado",
    ]


def test_extract_page_content_joins_blocks(monkeypatch) -> None:
    monkeypatch.setattr(
        notion,
        "extract_blocks_recursive",
        lambda page_id: [
            "Primer bloque",
            "Segundo bloque",
        ],
    )

    result = notion.extract_page_content("page-1")

    assert result == "Primer bloque\n\nSegundo bloque"


def test_extract_page_title_joins_title_fragments() -> None:
    page = {
        "properties": {
            "title": {
                "title": [
                    {"plain_text": "Receta: "},
                    {"plain_text": "Paella valenciana"},
                ]
            }
        }
    }

    result = notion.extract_page_title(page)

    assert result == "Receta: Paella valenciana"


def test_load_notion_page_returns_knowledge_document(monkeypatch) -> None:
    page = {
        "id": "page-123",
        "properties": {
            "title": {
                "title": [
                    {"plain_text": "CloudOps Notion Page"}
                ]
            }
        },
    }

    fake_client = SimpleNamespace(
        pages=SimpleNamespace(
            retrieve=lambda page_id: page,
        )
    )

    monkeypatch.setattr(
        notion,
        "client",
        fake_client,
    )

    monkeypatch.setattr(
        notion,
        "extract_page_content",
        lambda page_id: "Contenido de Notion",
    )

    document = notion.load_notion_page("page-123")

    assert document.document_id == "page-123"
    assert document.content == "Contenido de Notion"

    assert document.metadata == {
        "document_id": "page-123",
        "source": "notion://page-123",
        "title": "CloudOps Notion Page",
        "source_type": "notion",
    }