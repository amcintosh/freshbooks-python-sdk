from typing import Optional
from freshbooks.api.projects import ProjectsResource


class CommentsResource(ProjectsResource):
    """Handles resources under the `/comments` endpoints.

    These are handled identically to `/projects` endpoints.
    Refer to `freshbooks.api.projects.ProjectsResource`.
    """

    def _get_url(self, business_id: int, resource_id: Optional[int] = None, is_list: Optional[bool] = False) -> str:
        if resource_id:
            return "{}/comments/business/{}/{}/{}".format(
                self.base_url, business_id, self.single_resource_path, resource_id)
        if is_list:
            return "{}/comments/business/{}/{}".format(self.base_url, business_id, self.list_resource_path)
        return "{}/comments/business/{}/{}".format(self.base_url, business_id, self.single_resource_path)
