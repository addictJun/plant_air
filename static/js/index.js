// 更新时间
(function(){
    var t = null;
    t = setTimeout(time, 1000);//開始运行
    function time() {
        clearTimeout(t);//清除定时器
        dt = new Date();
        var y = dt.getFullYear();
        var mt = dt.getMonth() + 1;
        var day = dt.getDate();
        var h = dt.getHours();//获取时
        var m = dt.getMinutes();//获取分
        var s = dt.getSeconds();//获取秒
        document.querySelector(".showtime").innerHTML = '当前时间：' + y + "年" + mt + "月" + day + "-" + h + "时" + m + "分" + s + "秒";
        t = setTimeout(time, 1000); //设定定时器，循环运行     
    }
})();

// 模块滑动动画
(function(){
    var qiehuan = 0;
    function update_kepu() {
        
        if(qiehuan == 0){
            var div1 = document.getElementById('kepu2'); 
            div1.style.left = '0px';

            //移出div
            var div = document.getElementById('kepu1'); 
            for (let index = 0; index < 600; index++) {
                setTimeout(()=>{
                    div.style.left =  index+1 + 'px';
                },index*10/3)
            }

            // 左边视图
            $("#kepu1").fadeOut(1000);
            $("#kepu2").fadeIn(3000);

            //右边
            $("#0").slideToggle(2500) 
            setTimeout(function(){$("#1").slideToggle(2000)}, 500)
            setTimeout(function(){$("#2").slideToggle(1500)}, 1000)
            $("#012").fadeIn(3000);   

        } 
        else if(qiehuan == 1){

            var div1 = document.getElementById('kepu1'); 
            div1.style.left = '0px';

            //移出div
            var div = document.getElementById('kepu2'); 
            for (let index = 0; index < 600; index++) {
                setTimeout(()=>{
                    div.style.left =  index+1 + 'px';
                },index*10/3)
            }

            // 设置淡入淡出
            $("#kepu2").fadeOut(1000);
            $("#kepu1").fadeIn(3000);


            //滑出
            $("#0").slideToggle(1500) 
            $("#1").slideToggle(2000)
            $("#2").slideToggle(2500)
            $("#012").fadeOut(1000);
        }
        qiehuan = qiehuan + 1;
        if(qiehuan == 2){
            qiehuan = 0;
        }
    }
    window.setInterval(update_kepu, 20000);
})();

// 更新主界面

// //
// (function(){

// })();