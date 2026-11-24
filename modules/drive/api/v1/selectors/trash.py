from modules.drive.api.v1.selectors.file import FileSelector
from modules.drive.api.v1.selectors.folder import FolderSelector
from modules.drive.models import File, Folder


class TrashSelector:
    @staticmethod
    def list_for_user(user_id: int) -> dict[str, list[Folder] | list[File]]:
        return {
            "folders": list(FolderSelector.trashed_for_user(user_id)),
            "files": list(FileSelector.trashed_for_user(user_id)),
        }
