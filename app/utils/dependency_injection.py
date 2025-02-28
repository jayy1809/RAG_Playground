from usecases.file_upload_usecase import file_upload_usecase
from controllers.file_upload_controller import file_upload_controller

class dependency_injection:
    def get_file_upload_controller(self):
        usecase = file_upload_usecase()
        return file_upload_controller(usecase)