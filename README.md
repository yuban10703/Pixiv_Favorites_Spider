<h1 class="xsj_heading_hash xsj_heading xsj_heading_h1" id="pixiv_download_to_mongodb_1"
data-source-line="0" data-source-line-display="true">
  <div class="xiaoshujiang_element xsj_anchor">
    <a name="pixiv_download_to_mongodb_1" class="blank_anchor_name"></a>
    <a id="pixiv_download_to_mongodb_1" class="blank_anchor_id"></a>
    <a name="pixiv_download_to_mongodb" class="blank_anchor_name"></a>
    <a id="pixiv_download_to_mongodb" class="blank_anchor_id"></a>
  </div>
  <span class="xsj_heading_content">Pixiv_download_to_mongodb</span>
</h1>
<h2 class="xsj_heading_hash xsj_heading xsj_heading_h2" id="e5ae89e8a385_2" data-source-line="2"
data-source-line-display="true">
  <div class="xiaoshujiang_element xsj_anchor">
    <a name="e5ae89e8a385_2" class="blank_anchor_name"></a>
    <a id="e5ae89e8a385_2" class="blank_anchor_id"></a>
    <a name="安装" class="blank_anchor_name"></a>
    <a id="安装" class="blank_anchor_id"></a>
  </div>
  <span class="xsj_heading_content">安装</span>
</h2>
<p class="xsj_paragraph xsj_paragraph_level_0" data-source-line="3" data-source-line-display="true">python3.7+环境
  <br> mongodb
</p>
<h2 class="xsj_heading_hash xsj_heading xsj_heading_h2" id="e4bdbfe794a8e8afb4e6988e_3"
data-source-line="6" data-source-line-display="true">
  <div class="xiaoshujiang_element xsj_anchor">
    <a name="e4bdbfe794a8e8afb4e6988e_3" class="blank_anchor_name"></a>
    <a id="e4bdbfe794a8e8afb4e6988e_3" class="blank_anchor_id"></a>
    <a name="使用说明" class="blank_anchor_name"></a>
    <a id="使用说明" class="blank_anchor_id"></a>
  </div>
  <span class="xsj_heading_content">使用说明</span>
</h2>
<p class="xsj_paragraph xsj_paragraph_level_0" data-source-line="7" data-source-line-display="true">把库装好
  <br> 填上账号密码,配置好数据库应该就可以爬自己收藏夹里的色图了.....
  <br> 然后用下载脚本下载色图(下载和存数据库都会自动去重的)
  <br> 默认不是下载原图,下载的是"large"里的链接
  <br> 由于下载的图片都是webp格式的,PC端的QQ不能显示,所以用转换脚本再转换一下
</p>
<p class="xsj_paragraph xsj_paragraph_level_0" data-source-line="13" data-source-line-display="true">然后iotbot通过api调用数据库里的信息,再去对应路径找图片,再转换成base64上传发送....</p>
<p class="xsj_paragraph xsj_paragraph_level_0" data-source-line="16" data-source-line-display="true">有问题可以提issue</p>