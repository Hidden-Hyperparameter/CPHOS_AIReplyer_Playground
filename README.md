# As a Package

This project now become a package.

```shell
conda create -n CPHOS "python==3.8"
conda activate CPHOS # Or source activate CPHOS
pip install -r requirements.txt
```

Then you can use the package as follows:

```shell
cd ..
python -m your_folder_name.test # This runs test.py in the package. If you want to run other files, you can replace test with the file name.
```

## The old README.md is as follows

(**Notice** that due to the change, the code in this README may **NOT** be able to run. To run them, follow the instructions above.)

# 项目简介

使用的python版本为3.8.0。推荐使用conda进行包与环境的管理。

使用前，请先安装对应版本的python，随后安装requirements.txt中记录的包。然后可以使用glm_utils以及gpt_utils中定义的函数来调用glm、gpt；同时，使用search_pdf_utils.py中定义的函数来调用语言模型，可以获取指定pdf中与问题语义相近的部分。这一部分pdf语义匹配的代码来自于chatpdf。

注意，我们使用了tensorflow==2.11.0，这一版本的tf已经不再支持windows调用gpu。理论上，用tensorflow==2.10.0也是可以的而且支持调用windowsgpu。但为什么我这里写了2.11.0呢？因为cpu调用虽然慢但是跑得通，我这里用tf=2.10.0会有一点点小问题没法用gpu跑，所以干脆就写了2.11.0。如果大家用2.10.0+gpu跑的通了，请和我说一下然后我就改成2.10.0，毕竟用gpu跑神经网络会快很多。



## 他们各自的使用方法：

### db_api

可以连接到我们阅卷系统的数据库中。

数据库的地址、密码等存放在db_api/dbinformation.txt中。

CPHOS技术组之前结合我们后台数据库的模式，对mysql语句进行了一些封装，我们这里仅仅使用DataQueryApi（我删除了DataManagingApi的部分），并且请确保最后不commit。具体使用方式可以参考db_api_doc。我们目前打算开放给智能客服的权限只有查询权限，没有更改数据库信息的权限。

具体的每个api的文档，请参考`db_api_doc.pdf`。有一个样例叫做`example_dbapi.py`，可以使用

```shell
python -m your_folder_name.example_dbapi
```

运行。

### search_pdf_utils

可以通过定义`recommender`。注意，初次使用时，会自动下载一个约数百MB的网络参数，这时需要使用vpn。初次下载完成后，理论上后续调用就不需要重新下载该网络了。

可以通过调整search_pdf_utils.py中的batch, n_neighbors, word_length参数来调整返回的列表中每一个搜索结果的长度、搜索结果的个数。具体可以参考代码以及详细的注释是`example_searchpdf.py`，你可以在配置好环境之后直接用：

```shell
python -m your_folder_name.example_searchpdf
```

去运行它。请仔细阅读该样例的代码以及注释、运行结果。

### glm_utils:

具体可以参考代码以及详细的注释是`example_glm.py`，你可以用

```shell
python -m your_folder_name.example_glm
```

来运行它。请仔细阅读该样例的代码以及注释、运行结果。

### gpt_utils:

具体可以参考代码以及详细的注释是`example_gpt.py`，你可以用

```shell
python -m your_folder_name.example_gpt
```

来运行它。请仔细阅读该样例的代码以及注释、运行结果。

## 需要做的：

（init03更新）

我们在frequent_requests/questions.txt里面有微信昵称&问题；在`test.py`里面写了测试的程序；需要完成的是`work_file.py`里面的`answer_user_question(user_wechat_nickname, user_question)`函数。可以使用`/utils`文件夹来存放一些写的封装的方法什么的，可以避免把全部东西都写在`work_file.py`一个文件夹里。



**需要完成的就是`work_file.py`中的这个函数，然后可以把一些模块化的代码放在`/utils`中**然后在`work_file.py`里面import进来。（当然全放在这一个py文件里肯定也行，就是不太优雅）



**测试时，直接用：**

```shell
python -m your_folder_name.test
```

**即可将回答结果输出在`answers.txt`文件中。**





PS：

一种比较常见的answer_user_question的书写方式：

1. 获取信息
	1. pdf中的信息：可以通过search_pdf_utils，从pdf资料中获得接近问题的部分
	2. 系统中的信息：可以通过db_api_utils, 从阅卷系统的数据库中获得老师的信息
2. 编写prompt。将你以上获取到的信息，以及你对大语言模型的指令，共同编写成prompt，这个prompt就是喂给大语言模型的。
3. 从大语言模型（llm: LargeLanguageModel, gpt/glm就是其中之二）那里得到答案，并（直接或者处理后）返回。



一般而言，以上三步逐步可以回答一个问题。当然，如果效果好，你也可以设计两次llm的api调用，比如第一次先分类问题，第二次获取信息，返回答案等等。关键在于效果好。
