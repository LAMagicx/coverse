from fastapi import HTTPException, status

class BadRequestException(HTTPException):

    def __init__(self, exception: str == "", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(status_code=status_code, detail=exception)
