from pydantic import BaseModel


class BaseStyle(BaseModel):
    __hash__ = object.__hash__

    class Config:
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True

    def __enter__(self):
        self._original = self.model_copy(deep=True)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        for field_name in self.__pydantic_fields__.keys():
            original_value = getattr(self._original, field_name)
            setattr(self, field_name, original_value)

    @property
    def css_string(self) -> str:
        return " ".join([f'{k}="{v}"' for k, v in self.css().items()])
