"""Начальные колонки досок по пресетам — ROLES-AND-TASKS §7.2."""

from .models import WorkBoard, WorkColumn


def seed_columns_for_board(board: WorkBoard) -> None:
    """Создаёт колонки для новой доски (bulk_create)."""
    preset = board.preset
    rows: list[WorkColumn] = []

    if preset == WorkBoard.Preset.GENERIC_PM:
        spec = [
            ("Planned", "planned"),
            ("In progress", "in_progress"),
            ("Review", "review"),
            ("Paused", "paused"),
            ("Done", "done"),
            ("Cancelled", "cancelled"),
        ]
        for pos, (title, sem) in enumerate(spec):
            rows.append(WorkColumn(board=board, title=title, semantic=sem, position=pos))
    elif preset == WorkBoard.Preset.IT_SDLC:
        spec = [
            ("Backlog", "backlog"),
            ("Development", "development"),
            ("Testing", "testing"),
            ("Released", "released"),
        ]
        for pos, (title, sem) in enumerate(spec):
            rows.append(WorkColumn(board=board, title=title, semantic=sem, position=pos))
    else:
        rows.append(WorkColumn(board=board, title="Planned", semantic="planned", position=0))

    if rows:
        WorkColumn.objects.bulk_create(rows)
