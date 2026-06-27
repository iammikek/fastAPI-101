"""Application-specific exceptions."""


class ItemNotFoundError(Exception):
    """Raised when an item id does not exist."""

    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")
