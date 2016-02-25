
var page = $('.page');
var entry = $('.entry');
var message = $('.message');
var codebox = $('.codebox');
var CodeboxInput = $('.codebox-input');
var CodeboxOutput = $('.codebox-output-content');
var outputLine = $('<div>').addClass('codebox-output-line');
var user = {};
var userList;
var uid;
var mid = 0;
var checkMsgTimer;
var num;
var start = 0;
var energy = 0;
var status = -1;
var mycolor;
var roomData;
var userData;
var colors = [];
var serverURL = 'http://115.28.65.51:8080';

function getErrorMsg (status) {
	var msg = ['未知非法操作', 'success', 'method must be post', 'method must be get', 'uid is invalid', 'no authority to do', '房间已满', '房间不存在或游戏已经开始', '还没轮到您的回合', '指令有误,请重新输入', '游戏已经开始'];
	return msg[status];
}

function getMapString (length) {
	var mapString = '<table border="1">';
	var trString = '<tr height="' + 100 / length + '%">';
	var tdString = '<td width="' + 100 / length + '%"></td>';
	for (var i = 0; i < length; i++){
		trString += tdString;
	}
	for (var i = 0; i < length; i++){
		mapString += trString + '</tr>';
	}
	mapString += '</table>';
	return mapString;
}

function checkForm ($form) {
	var inputs = $form.children('input');
	return [].every.call(inputs, function(elem){
		//console.log(elem.hasAttribute('required'), elem.value, elem.value.trim() !== '')
		return elem.hasAttribute('required') ? elem.value.trim() !== '' : 1;
	});
}

function fetchForm ($form) {
	var inputs = $form.children('input');
	var data = {};
	[].forEach.call(inputs, function(elem){
		data[elem.getAttribute('name')] = elem.value.trim();
	});
	return data;
}

function outputLog (log, html) {
	var curLine = outputLine.clone();
	if (!html) curLine.text(log);
	else curLine.html(log);
	curLine.appendTo(CodeboxOutput);
}

function showRoom (id) {
	$('.number').text('No. ' + id);
	if (id == user.uid) $('.button-start').show();
	else $('.button-start').hide();
	CodeboxOutput.empty();
	$.ajax({
		method: 'POST',
		url: serverURL + '/room/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: id
		},
		success: function(data) {
			if (data.status != 1) return outputLog('进入房间失败：' + getErrorMsg(data.status));
			uid = id;
			$('.map').html(getMapString(data.info.length));
			outputLog('欢迎来到 BOMB ROOM！');
			outputLog('可用指令：<code>turnLeft()</code> 向左转<br>　　　　　<code>turnRight()</code> 向右转<br>　　　　　<code>goForward()</code> 向前走<br>　　　　　<code>putBomb()</code> 放下炸弹<br>　　　　　<code>endTurn()</code> 提前结束此回合', 1);
			outputLog('BOMB ROOM #' + id + '　房主：' + data.info.name + '　指令上限：' + data.info.energy + '　用户上限：' + data.info.capacity /*+ '　用户列表：' + data.info.players.join(', ') */+ ' (' + data.info.num + '/' + data.info.capacity +')');
			getLatestMsg();
		},
		dataType: 'json'
	});
}

function getLatestMsg () {
	clearTimeout(checkMsgTimer);
	$.ajax({
		method: 'POST',
		url: serverURL + '/query/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			mid: mid
		},
		success: function(data) {
			if (data.status != 1) return outputLog('获取消息失败：' + getErrorMsg(data.status));
			data.info.data.sort(function(a, b){
				return a.mid - b.mid;
			});
			for (var i = 0, j = data.info.data; i < j.length; i++) {
				outputLog(j[i].content);
				if (j[i].mid - 0 > mid - 0) mid = j[i].mid - 0;
			}
			// outputLine.clone().text().appendTo(CodeboxOutput);
			checkMsgTimer = setTimeout(getLatestMsg, 5000);
			$('.codebox-output').scrollTop(CodeboxOutput.height());
			userData = data.info;
			start && colorMap(data.info.order_id, data.info.position);
		},
		dataType: 'json'
	});
	if (!start) {
		$.ajax({
			method: 'POST',
			url: serverURL + '/room/',
			xhrFields: {
				withCredentials: true
			},
			data: {
				host: uid
			},
			success: function(data) {
				if (data.info.num != num) {
					outputLog('BOMB ROOM #' + uid + '　房主：' + data.info.name + '　指令上限：' + data.info.energy + '　用户上限：' + data.info.capacity /*+ '　用户列表：' + data.info.players.join(', ')*/ + ' (' + data.info.num + '/' + data.info.capacity +')');
					num = data.info.num;
				}
			},
			dataType: 'json'
		});
		if (uid != user.uid) checkStart();
	}
	else checkTurn();
}

function checkStart () {
	if (uid == user.uid || start) return;
	$.ajax({
		method: 'GET',
		url: serverURL + '/wait/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: uid
		},
		success: function(data) {
			if (data.status != 1) return;
			outputLog('游戏已开始。');
			start = 1;
			gameStart();
		},
		dataType: 'json'
	});
}

function checkTurn () {
	if (!start) return;
	$.ajax({
		method: 'GET',
		url: serverURL + '/turn/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: uid
		},
		success: function(data) {
			if (data.status == status) return;
			if (data.status == 1) outputLog('现在轮到您了。');
			else if (data.status == 7) {
				outputLog('您取得了最终的胜利！');
				start = 0;
			}
			status = data.status;
		},
		dataType: 'json'
	});
}

function gameStart() {
	$.ajax({
		method: 'POST',
		url: serverURL + '/room/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: uid
		},
		success: function(data) {
			if (data.status != 1) return outputLog('初始化失败：' + getErrorMsg(data.status));
			roomData = data.info;
//			for (var i = 0; i < data.info.num; i++) {
//				colors.push('rgb(' + Math.floor(Math.random() * 256) + ',' + Math.floor(Math.random() * 256) + ',' + Math.floor(Math.random() * 256) + ')');
//			}
            		colors = data.info.colors
			$('.map').html(getMapString(data.info.length));
			outputLog('BOMB ROOM #' + uid + '　房主：' + data.info.name + '　指令上限：' + data.info.energy + '　用户上限：' + data.info.capacity + '　用户列表：' + data.info.players.map(function(elem, index){
				return '<span style="color: ' + colors[index] + '">' + elem + '</span>';
			}).join(', ') + ' (' + data.info.num + '/' + data.info.capacity +')', 1);
			// data.info.ids.filter(function(elem, uid){
			// 	mycolor = colors[uid];
			// })[0];
			mycolor = colors[data.info.ids.indexOf(user.uid)];
			alert(mycolor);
			outputLog('<span style="color: ' + mycolor + '">这是您的颜色</span>', 1);
			start = 1;
			getLatestMsg();
		},
		error: function (e) {
			return message.addClass('show').text('HTTP Error ' + e.status + ': ' + e.statusText);
		},
		dataType: 'json'
	});
}

function colorMap (order, position) {
	$('.map').html(getMapString(roomData.length));
	for (var i = 0; i < order.length; i++) {
		$('.map tr').eq(position[i].split(',')[0]).children('td').eq(position[i].split(',')[1]).css('background', colors[i]);
	}
}

entry.on('click', 'button', function (event) {
	var target = $(event.target);
	var type = target.data('type');
	if (page[0].dataset.action !== type) {
		page.attr('data-action', type);
		$('.form').each(function(){
			var that = $(this);
			if (that.hasClass('form-' + type)) {
				that.find('input').each(function(){
					$(this).removeAttr('tabIndex');
				});
			}
			else {
				that.find('input').each(function(){
					$(this).attr('tabIndex', '-1');
				});
			}
		});
		message.text('').removeClass('show');
	}
	else {
		if (type !== 'return') {
			var form = $('.form-' + type);
			form.find('button').click();
		}
	}
});

$('.form-access').on('submit', function (event) {
	event.preventDefault();
	var form = $('.form-access');
	message.addClass('show').text('正在提交数据......');
	if (!checkForm(form)) return ((message.text('请完整填写表单')) && setTimeout(function(){
		message.text('').removeClass('show');
	}, 2000));
	var formData = fetchForm(form);
	$.ajax({
		method: 'POST',
		url: form.attr('action').replace(/\{serverURL\}/, serverURL),
		xhrFields: {
			withCredentials: true
		},
		data: formData,
		success: function(data) {
			if (data.status != 1) return message.addClass('show').text('提交失败：' + getErrorMsg(data.status));
			user = data.info;
			message.removeClass('show').text('');
			page.removeClass('access-page').addClass('front-page');
		},
		error: function (e) {
			return message.addClass('show').text('HTTP Error ' + e.status + ': ' + e.statusText);
		},
		dataType: 'json'
	});
	return false;
});

$('.form-create').on('submit', function (event) {
	event.preventDefault();
	var form = $('.form-create');
	message.addClass('show').text('正在提交数据......');
	if (!checkForm(form)) return ((message.text('请完整填写表单')) && setTimeout(function(){
		message.text('').removeClass('show');
	}, 2000));
	var formData = fetchForm(form);
	formData['uid'] = user.uid;
	//console.log(formData)
	$.ajax({
		method: 'POST',
		url: form.attr('action').replace(/\{serverURL\}/, serverURL),
		xhrFields: {
			withCredentials: true
		},
		data: formData,
		success: function(data) {
			if (data.status != 1) return message.text('提交失败：' + getErrorMsg(data.status));
			formData.host = user.uid;
			$.ajax({
				method: 'POST',
				url: serverURL + '/change/',
				xhrFields: {
					withCredentials: true
				},
				data: formData,
				success: function(data) {
					if (data.status != 1) return message.text('提交失败：' + getErrorMsg(data.status));
					message.textContent = '创建成功！';
					uid = user.uid;
					setTimeout(function(){
						page.removeClass('front-page').addClass('room-page');
						showRoom(user.uid);
					}, 1000);
				},
				error: function (e) {
					return message.addClass('show').text('HTTP Error ' + e.status + ': ' + e.statusText);
				},
				dataType: 'json'
			});
		},
		dataType: 'json'
	});
	return false;
});

$('.form-enter').on('submit', function (event) {
	event.preventDefault();
	var form = $('.form-enter');
	message.addClass('show').text('正在提交数据......');
	if (!checkForm(form)) return ((message.text('请完整填写表单')) && setTimeout(function(){
		message.text('').removeClass('show');
	}, 2000));
	var formData = fetchForm(form);
	$.ajax({
		method: 'POST',
		url: form.attr('action').replace(/\{serverURL\}/, serverURL),
		xhrFields: {
			withCredentials: true
		},
		data: formData,
		success: function(data) {
			if (data.status != 1) return message.text('提交失败：' + getErrorMsg(data.status));
			uid = formData.host;
			page.removeClass('front-page').addClass('room-page');
			showRoom(uid);
		},
		error: function (e) {
			return message.addClass('show').text('HTTP Error ' + e.status + ': ' + e.statusText);
		},
		dataType: 'json'
	});
	return false;
});

CodeboxInput.on('keypress', function (event) {
	// CodeboxInput.text(CodeboxInput.text()); // 去除 HTML 标签
	if (event.keyCode === 13) {
		var value = CodeboxInput.text().trim();
		outputLog('<code>' + value.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code>', 1);
		CodeboxInput.text('');
		if (value !== '') {
			$.ajax({
				method: 'POST',
				url: serverURL + '/action/',
				xhrFields: {
					withCredentials: true
				},
				data: {
					move: value
				},
				success: function(data) {
					if (data.status != 1) return outputLog('提交失败：' + getErrorMsg(data.status));
					getLatestMsg();
					//outputLog(data.info.content);
				},
				error: function (e) {
					return outputLog('HTTP Error ' + e.status + ': ' + e.statusText);
				},
				dataType: 'json'
			});
		}
	}
});

$('.button-start').on('click', function (event) {
	if (uid == null) return;
	$.ajax({
		method: 'GET',
		url: serverURL + '/start/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: uid
		},
		success: function(data) {
			if (data.status != 1) return outputLog('提交失败：' + getErrorMsg(data.status));
			outputLog('您开始了游戏。');
			gameStart();
			getLatestMsg();
			$('.button-start').hide();
		},
		error: function (e) {
			return outputLog('HTTP Error ' + e.status + ': ' + e.statusText);
		},
		dataType: 'json'
	});
});

$('.button-leave').on('click', function (event) {
	if (uid == null) return;
	confirm('您确定要离开房间么？') && $.ajax({
		method: 'POST',
		url: serverURL + '/leave/',
		xhrFields: {
			withCredentials: true
		},
		data: {
			host: uid
		},
		success: function(data) {
			if (data.status != 1) return outputLog('提交失败：' + getErrorMsg(data.status));
			uid = null;
			outputLog('您已离开游戏！');
			page.removeClass('room-page').addClass('front-page');
		},
		error: function (e) {
			return outputLog('HTTP Error ' + e.status + ': ' + e.statusText);
		},
		dataType: 'json'
	});
});
