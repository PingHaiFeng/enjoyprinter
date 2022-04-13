﻿using System;
using System.Collections.Generic;

using System.Drawing;
using System.Net;
using System.Text;
using System.Windows.Forms;
using System.IO;

using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using WinFormsApp1;
using System.Threading;
using System.Threading.Tasks;
using CloudPrint;
using CloudPrint.Api;
using System.Runtime.Serialization.Formatters.Binary;
using CloudPrint.Entity;
using System.Runtime.InteropServices;
using System.Drawing.Text;

namespace 云打印
{
    public partial class FormLogin : Form
    {
        

     
        TcpClient tcpClient = null;
        TcpClient tcpClient2 = null;
        private static Thread heartThread;
        private Boolean IsLogin = false;
       
        public FormLogin()
        {
            InitializeComponent();
            //从外部文件加载字体文件  
            PrivateFontCollection font = new PrivateFontCollection();

            font.AddFontFile( @"..\..\..\asset\腾讯体-Medium.TTF");
            //检测字体类型是否可用
            var r = font.Families[0].IsStyleAvailable(FontStyle.Regular);
            var b = font.Families[0].IsStyleAvailable(FontStyle.Bold);
            //定义成新的字体对象
            FontFamily myFontFamily = new FontFamily(font.Families[0].Name, font);
            Font myFont = new Font(myFontFamily, 27, FontStyle.Bold);
            //将字体显示到控件  
            labTitle.Font = myFont;
           
            labTitle.Parent = this.pictureBox3;

        }

        private void Form_login_Load(object sender, EventArgs e)
        {
            Console.WriteLine(AppDomain.CurrentDomain.SetupInformation.ApplicationBase);
            this.Show();
            labTitle.Parent = this.pictureBox3;
            ReadUserLoginConfig();
        }

        private void tbPassword_KeyPress(object sender, KeyPressEventArgs e)
        {

            if (e.KeyChar == 13) Login();


        }

        private void btn_login_Click(object sender, EventArgs e)
        {

            Login();

        }


        private void Login()
        {
            if (tbUsername.Text == "" || tbPassword.Text == "")
            {
                labLoginTip.Text = "请输入账号及密码";
                labLoginTip.ForeColor = Color.Red;
                return;
            }

            btnLogin.Text = "登录中...";
            
            btnLogin.ForeColor = Color.White;
            JObject resData = UserApi.Login(tbUsername.Text, tbPassword.Text);
            Console.WriteLine(resData);
            String stateCode = resData["state"].ToString();

           if(stateCode=="1")
            {
                string token = resData["data"]["token"].ToString();//连接Token
                GlobalData.token = token;//保存token到全局变量
                GlobalData.UserName = tbUsername.Text;//保存token到全局变量
                GetStoreInfo(token);

            }
            else
            {
                labLoginTip.Text = "账号或密码错误";
                labLoginTip.ForeColor = Color.Red;
                btnLogin.Text = "登录";
            }
        }

        private void GetStoreInfo(string token)
        {
            JObject resData = UserApi.GetStoreInfo(token);
            String stateCode = resData["state"].ToString();
            if (stateCode == "1")
            {
                string store_name = resData["data"]["store_name"].ToString();
                string store_id = resData["data"]["store_id"].ToString();
                GlobalData.store_name = store_name; //保存店铺名称到全局变量
                GlobalData.store_id = store_id;     //保存店铺名称到全局变量
                JObject resData2 = PrinterApi.SetPrintersInfo(store_id);
                String stateCode2 = resData2["state"].ToString();
                if (stateCode2 == "1")
                {
                    SaveLoginConfig();
                    StartConn();

                }

            }
        }

        /// <summary>
        /// 记住密码
        /// </summary>
        private void SaveLoginConfig()
        {
            try
            {
                User user = new User();
                FileStream fs = new FileStream("data.bin", FileMode.OpenOrCreate);
                BinaryFormatter bf = new BinaryFormatter();
                user.UserName = tbUsername.Text.Trim();
                user.RememberPwd = checkBoxRememberPwd.Checked;
                if (user.RememberPwd) user.PassWord = tbPassword.Text.Trim();
                else user.PassWord = "";
                user.AutoLogin = checkBoxAutoLogin.Checked;
                bf.Serialize(fs, user);
                fs.Close();
            }
            catch { }
        }

        /// <summary>
        /// 读取本地登录配置
        /// </summary>
        public void ReadUserLoginConfig()
        {
            try
            {
                FileStream fs = new FileStream("data.bin", FileMode.OpenOrCreate);

                if (fs.Length > 0)
                {

                    User user = new User();
                    BinaryFormatter bf = new BinaryFormatter();
                    user = bf.Deserialize(fs) as User;
                    tbUsername.Text = user.UserName;
                    tbPassword.Text = user.PassWord;
                    checkBoxRememberPwd.Checked = user.RememberPwd;
                    checkBoxAutoLogin.Checked = user.AutoLogin;
                    fs.Close();
                    if (checkBoxAutoLogin.Checked && tbPassword.Text.Length > 0)
                    {

                        Login();
                        return;
                    }
                }
                fs.Close();
            }
            catch 
            {
                Console.WriteLine("出错");
                return;
            }

        }
        public void StartConn()
        {

            Instruct instruct_data = new Instruct();
            instruct_data.instruct_id = 2001;
            instruct_data.instruct_content = "客户端尝试连接服务器";
            instruct_data.instruct_dict = new Dictionary<string, object>();
            instruct_data.instruct_dict.Add("token", GlobalData.token);
            instruct_data.instruct_dict.Add("store_id", GlobalData.store_id);
            string instruct_data_str = JsonConvert.SerializeObject(instruct_data);//对象转字符串
            tcpClient = new TcpClient();
            tcpClient.Send(instruct_data_str);
            heartThread = new Thread(tcpClient.SendAliveHeart);//心跳线程
            heartThread.IsBackground = true;
            heartThread.Start();
            OpenMainWindow();
        }

        void OpenMainWindow()
        {
            FormMain formMain = new FormMain();
            Hide();
            //GlobalData.form_main = formMain;
            formMain.ShowDialog();
            Application.ExitThread();

        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void btn_close_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }







        private void label5_Click(object sender, EventArgs e)
        {

        }

        private void lab_title_Click(object sender, EventArgs e)
        {

        }

        private void pictureBox3_Click(object sender, EventArgs e)
        {

        }

        private void tbPassword_TextChanged(object sender, EventArgs e)
        {

        }

        private void checkBoxRemember_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void tbUsername_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
