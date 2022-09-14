# 导入OS模块
import os


def _findLogfiles(path, res):
    # 首先遍历当前目录所有文件及文件夹
    path = os.path.abspath(path)
    file_list = os.listdir(path)
    # 循环判断每个元素是否是文件夹还是文件，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            _findLogfiles(cur_path, res)
        else:
            # 判断是否是特定文件名称
            if file.endswith('.rcg'):
                res.append(os.path.join(path, file))


def findAllLogfiles(path):
    res = []
    _findLogfiles(path, res)
    return res


if __name__ == '__main__':
    result = findAllLogfiles('../log')
    print(result)
