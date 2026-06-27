"""Application-specific exceptions."""


class ItemNotFoundError(Exception):
    """Raised when an item id does not exist."""

    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")


class CategoryNotFoundError(Exception):
    """Raised when a category id does not exist."""

    def __init__(self, category_id: int) -> None:
        self.category_id = category_id
        super().__init__(f"Category {category_id} not found")


class CategoryInUseError(Exception):
    """Raised when a category cannot be deleted because items reference it."""

    def __init__(self, category_id: int) -> None:
        self.category_id = category_id
        super().__init__(f"Category {category_id} has items and cannot be deleted")


class CategoryNameExistsError(Exception):
    """Raised when a category name is already taken."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Category name '{name}' already exists")
