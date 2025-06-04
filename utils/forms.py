from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
class BootstrapModelForm(forms.ModelForm):
    # 好几个表都会用此样式集成到一块
    exclude_form=[]
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        for name,field in self.fields.items():
            # if name=="password":
            #     continue  也可以分类设计
            #                       循环加样式
            if name in self.exclude_form:
                continue
            if field.widget.attrs!=None:  #如果以前有样式 别把之前的冲掉
                field.widget.attrs['class']='form-control'
                field.widget.attrs['placeholder']=field.label
            else:
                field.widget.attrs={"class":"form-control","placeholder":field.label}

            # if name=="create_time":
            #     field.widget.attrs = {"id": "dt","class":"form-control","placeholder":field.label}

#后面用form继承这个  modelform继承上面
class BootstrapForm(forms.Form):
    exclude_form=[]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        for name,field in self.fields.items():
            if name in self.exclude_form:
                continue
            # if name=="password":
            #     continue  也可以分类设计
            #                       循环加样式
            if field.widget.attrs!=None:  #如果以前有样式 别把之前的冲掉
                field.widget.attrs['class']='form-control'
                field.widget.attrs['placeholder']=field.label
            else:
                field.widget.attrs={"class":"form-control","placeholder":field.label}
