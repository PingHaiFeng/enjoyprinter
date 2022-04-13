'''打印小程序端路由'''
from flask import Blueprint, request, jsonify, redirect, url_for,send_from_directory
import time
from plugins.file_reader import readFiles
from socket_sever.handle_socket import send_to_server
import ast
from model.db_model.store import StoreAccount, db,Store,Printer,Price
from model.db_model.user import Order,FileOrder,db
from utils.utils import *
from model.db_model.admin import FeedBack,Partner
from model.db_model.library import Folder,Document
from utils.state_handler import *
from log.except_logger import *
from plugins.redis_serve import *
from view.mini.func.take_id import take_id_maker
mini = Blueprint('mini', __name__)  # 第一个蓝图名称，第二个参数表示蓝图所在板块

IO_PATH = get_relative_path()+ "\\temp_files\\"

#获取所选店铺资料
@mini.route('/store-info', methods=["POST", "GET"])
@except_logger
def get_store_info():
    store_id =request.args.get("store_id")
    host_ip = StoreAccount.query.filter_by(store_id=store_id).first().host_ip
    printers_params = model_to_dict(Printer.query.filter_by(store_id=store_id,host_ip=host_ip,can_self_print=1).all())
    price_list = model_to_dict(Price.query.filter_by(store_id=store_id).all())
    account_info = model_to_dict(Store.query.filter_by(store_id=store_id).first())
    pc_online=r.exists("ONLINE_STATE_"+store_id)
    store_info={
        "pc_online":pc_online,
        "printers_params":printers_params,
        "price_list":price_list,
        "account_info":account_info
    }
    return State.success(data={"store_info": store_info})


# 接收小程序上传的文件
@mini.route('/upload', methods=["POST", "GET"])
@except_logger
def upload():
    file = request.files.get("file")  # 待接收文件
    file_id = request.form.get("file_id")  # 文件id，特有标识
    file_name = request.form.get("file_name")  # 文件名带扩展名
    file_type = file_name.split(".")[-1]  # 文件扩展名
    file_new_name = file_id + '.' + file_type  # 新文件
    upload_platform = request.form.get("upload_platform")  # 平台类型
    if upload_platform == "MiniProgram":
        file_path = request.form.get("file_path")
    if upload_platform == "H5":
        file_path = 'https://enjoyprint.pinghaifeng.cn/mini/send_file/' + file_new_name
    with open(IO_PATH + file_new_name, "wb") as f:
        data = file.read()
        f.write(data)
    file_page_num, file_type_id = readFiles(file_new_name, file_name, file_type)  # 返回文件页数和文件图标路径
    none_suffix_fileName = file_name[::-1].split(".", 1)[-1][::-1]  # 取消后缀名
    data =  {
            "file_id": file_id,
            "file_name": none_suffix_fileName,
            "file_page_num": file_page_num,
            "file_type": file_type,
            "file_type_id": file_type_id,
            "file_path": file_path,
            "print_info": {"size": "A4", "print_color": 1, "duplex": 1, "print_count": 1,"is_print_all": 1, "print_from_page": 1,"print_to_page":file_page_num, "print_page_num": file_page_num}
        }
    return State.success(data=data)
    


# 执行打印
@mini.route("/exe_print", methods=["POST", "GET"])
@except_logger
def exe_print():
    if request.form.get("tempFile_list"):tempFile_list = ast.literal_eval(request.form.get("tempFile_list"))
    store_id = request.form.get("store_id")
    order_id = request.form.get("order_id")
    printer_name = request.form.get("printer_name")
    file_count = request.form.get("file_count")
    take_id = take_id_maker(store_id)
    host_ip = StoreAccount.query.filter_by(store_id=store_id).first().host_ip
    if host_ip:
        instruct_data = {
            "instruct_id":3002,
            "instruct_content":"transmit",
            "instruct_dict":{"goal_ip":host_ip,"take_id":take_id, "tempFile_list":tempFile_list,"printer_name":printer_name,"order_id":order_id,"file_count":file_count}
        }
        return send_to_server(instruct_data)
    else:
        return State.fail("无此店铺账号或未登陆激活")


# 生成订单
@mini.route('/set_orders', methods=["POST", "GET"])
@except_logger
def set_orders():
    tempFile_list=ast.literal_eval(request.form.get("tempFile_list"))
    openid = request.form.get("openid")
    store_id = request.form.get("store_id")
    order_id = request.form.get("order_id")
    take_id = request.form.get("take_id")
    order_type = request.form.get("order_type")
    printer_name = request.form.get("printer_name")
    price = request.form.get("price")
    file_count = request.form.get("file_count")
    for i in tempFile_list:
        file_id = i["file_id"]
        file_name = i["file_name"]
        duplex = i["print_info"]["duplex"]
        print_color = i["print_info"]["print_color"]
        print_count = i["print_info"]["print_count"]
        size = i["print_info"]["size"]
        print_price=float(i["print_price"])
        print_situation_code=-1
        print_situation="待打印"
        file_type = i["file_type"]
        file_type_id = i["file_type_id"]
        print_file = FileOrder(order_id=order_id,file_id=file_id,print_count=print_count,size=size, file_name=file_name,print_price=print_price,file_type=file_type,file_type_id=file_type_id,duplex=duplex,print_color=print_color)
        db.session.add(print_file)
        db.session.commit()
    orders = Order(order_id=order_id,order_type=order_type,store_id=store_id,file_count=file_count, printer_name=printer_name,price=price,print_situation_code=print_situation_code, print_situation=print_situation,take_id=take_id, openid=openid)
    db.session.add(orders)
    db.session.commit()
    return State.success()




# 获取订单
@mini.route("/order-list", methods=["GET"])
@except_logger
def get_orders():
    openid = request.headers["OpenID"]
    list = model_to_dict(Order.query.filter_by(openid=openid).order_by(Order.create_time.desc()).all())
    return State.success(data={"list": list})

# 获取文件订单
@mini.route("/file-order-list", methods=["GET"])
@except_logger
def get_file_orders():
    order_id = request.args.get("order_id")
    list = model_to_dict(FileOrder.query.filter_by(order_id=order_id).order_by(FileOrder.create_time.desc()).all())
    return State.success(data={"list": list})


# 获取店铺列表
@mini.route('/store-list', methods=["POST", "GET"])
@except_logger
def list_store():
    list =  model_to_dict(Store.query.all())
    return State.success(data={"list": list})


# 获取所选店铺信息
@mini.route('/online-state', methods=["POST", "GET"])
@except_logger
def get_store_selected():
    store_id = request.form.get("store_id")
    if r.exists("ONLINE_STATE_"+store_id)==1:
        return State.success()
    else:
        return State.fail()

# 下载文件
@mini.route("/send_file/<file_new_name>", methods=["POST", "GET"])
def send_file(file_new_name):
    Path = get_relative_path()+ "\\temp_files"
    return send_from_directory(Path, file_new_name, as_attachment=True)


# 用户建议
@mini.route('/advice', methods=["POST", "GET"])
@except_logger
def user_advice():
    db.session.add(FeedBack(request.form))
    db.session.commit()
    return State.success()



# 用户入驻
@mini.route('/partner_settle', methods=["POST", "GET"])
@except_logger
def partner_settle():
    db.session.add(Partner(request.form))
    db.session.commit()
    return State.success()



# 获取文库文件夹列表
@mini.route('/list-folder', methods=["POST", "GET"])
@except_logger
def list_folder():
    list =  model_to_dict(Folder.query.all())
    return State.success(data={"list": list})



# 获取文件列表
@mini.route('/list-doc', methods=["POST", "GET"])
@except_logger
def list_doc():
    folder_id=request.form.get("folder_id")
    print(folder_id)
    list =  model_to_dict(Document.query.filter_by(folder_id=folder_id).order_by(Document.ishot.desc()).all())
    return State.success(data={"list": list})

    
# 文库文件打印参数
@mini.route('/lib-print', methods=["POST", "GET"])
@except_logger
def lib_print():
    id = request.args.get("id")
    res = Document.query.filter_by(id=id).first()
    
    data = {
            "file_id": res.file_id,
            "file_name": res.name,
            "file_page_num": res.file_page_num,
            "file_type": res.file_type,
            "file_type_id": res.file_type_id,
            "file_path": res.url,
            "print_info": {"size": "A4", "print_color": 1, "duplex": 1, "print_count": 1,"is_print_all": 1, "print_from_page": 1,"print_to_page":res.file_page_num, "print_page_num": res.file_page_num}
        }
    return State.success(data=data)



@mini.after_request
def releaseDB(response):
    db.session.close()
    return response