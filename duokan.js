var system = require('system');
var fs = require('fs');
var page = require('webpage').create();

if (system.args.length < 3) {
    console.log('Usage:');
    console.log('phantomjs book.js BOOKID FOLDER FORMAT')
    console.log('BOOKID: id from url; FOLDER: where to save files;');
    console.log('FORMAT: Optional, input value 1 or 2, default is 2');

    phantom.exit()
}

var BOOK_URL = 'http://www.duokan.com/reader/www/app.html?id=' + system.args[1];

var FOLDER = system.args[2];

//set view port size
if (1 == system.args[3]) {
    page.viewportSize = {width: 800, height: 1600};
} else if (2 == system.args[3]) {
    page.viewportSize = {width: 2560, height: 1600};
} else if (3 == system.args[3]) {
    page.viewportSize = {width: 800, height: 1000};
} else if (4 == system.args[3]) {
    page.viewportSize = {width: 1000, height: 1000};
} else {
    page.viewportSize = {width: 2560, height: 1600};
}

//set cookie
page.cookies = {
	'Hm_lpvt_1c932f22da573f2870e8ab565f4ff9cb':'1439872326',
	'Hm_lvt_1c932f22da573f2870e8ab565f4ff9cb':'1439341102,1439456817,1439872309',
	'app_id':'web',
	'bdshare_firstime':'1439341178602',
	'channel':'49PXVQ',
	'device_id':'D900D0W8AFXY05P0',
	'last_uid':'40PDtzyqv1BOwvMQwJSbZ82_8Ya70mC-1RHd_zCWTma9aJvKnraK7se4Yn_5r956',
	'last_user':'3924881',
	'name':'vin',
	'reader_preference':'horizontal',
	'store_noob':'check',
	'thumbnail':'http://dl2.files.xiaomi.net/mfsv2/avatar/s010/p01SmUxJxtAY/GO2BDMwF4M5RVU.jpg',
	'token':'40PDtzyqv1BOwvMQwJSbZ82_8Ya70mC-1RHd_zCWTma9aJvKnraK7se4Yn_5r956',
	'userId':'40PDtzyqv1BOwvMQwJSbZ82_8Ya70mC-1RHd_zCWTma9aJvKnraK7se4Yn_5r956',
	'user_id':'3924881'
};

var _padding = function(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
};

var _pageNum = 1;
var _getPageNum = function() {
    return _padding(_pageNum++, 4);
};

var _isTextLoaded = function() {
    return page.evaluate(function() {
        return window['jQuery'] ? 0 == jQuery('.loading').length : false;
    });
};

var _closeAd = function() {
    page.evaluate(function() {
        if (0 != jQuery('.u-btn.j-close')) {
            jQuery('.u-btn.j-close').click();
            console.log('closed AD');
        }
    });
};

var _closeHelper = function() {
    page.evaluate(function() {
        jQuery('.j-md-help').hide();
    });
};

var _isEnd = function() {
    return page.evaluate(function() {
        var footers = jQuery('.j-md-footer div');
        if (footers.length > 0) {
            var last = footers[footers.length - 1];
            var texts = $(last).text().split('/');
            if (2 == texts.length) {
                return texts[0] == texts[1];
            }
        }

        return false;
    });
};

var _getProgress = function() {
	var prog = page.evaluate(function() {
		return $('.left').text()
	});
	
	console.log('progress, '+prog)
};

var _nextPage = function() {
    page.evaluate(function() {
        jQuery('.j-pagedown').click();
    });
};

var _setClipRect = function(page) {
    var rect = page.evaluate(function() {
        return $('.j-md-book')[0].getBoundingClientRect();
    });

    page.clipRect = {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
    };
    // console.log('T:'+rect.top+',L:'+rect.left+',W:'+rect.width+',H:'+rect.height);
};

var _setPaperSize = function(page) {
    page.paperSize = {
        width: '667px',
        height: '889px'
    };
};

var _renderBook = function() {
    var timeout = 0;
    var interval = 1000;
    var timer = setInterval(function() {
        if (_isTextLoaded() && _isPicLoaded()) {
            _closeAd();
            _closeHelper();
            var pageNum = _getPageNum();
            var fileName = FOLDER + '/' + pageNum + '.pdf';
            _setClipRect(page);
            page.render(fileName);
            //console.log(fileName);

            _getProgress()

            if (_isEnd()) {
                clearInterval(timer);
                phantom.exit()
            } else {
                _nextPage();
            }

            timeout = 0;
        } else if(timeout > 40 * 1000){
            console.log("refresh page, because of timeout")
            _refreshPage();
            timeout = 0;
        } else {
            timeout += interval;
        }
    }, interval);
};


var _isMatchedUrl = function(url) {
    
    if (/duokan\.com/.test(url)) {
        return true;
    } else {
        return false;
    }
};

var _objectSize = function(obj) {
    var size = 0;
    var key;
    for(key in obj){
        if(obj.hasOwnProperty(key)){
            size++;
        }
    }
    return size;
};

var _pics = {};

var _refreshPage = function() {
    page.open(BOOK_URL, function(){
        _pics = {};
    });
};


var _isPicLoaded = function(callback) {
    if (0 == _objectSize(_pics)) {
        return true;
    } else {
        return false;
    }
};

String.prototype.startWith = function(s) {
    if (s == null || s == "" || this.length == 0 || s.length > this.length) {
        return false;
    }

    if (this.substr(0, s.length) == s) {
        return true;
    } else {
        return false;
    }

    return true;
 };

var _isImg2Ignore = function(url) {
    var url1 = "http://www.duokan.com/reader/www/images/beta.png";
    var url2 = "http://www.duokan.com/reader/www/images/reader-loading.png";
    var url3 = "http://www.duokan.com/reader/www/images/loading.gif";
    var url4 = "http://www.duokan.com/reader/www/images/reader.png";
    var url5 = "http://www.duokan.com/reader/www/images/shadow1.png";
    var url6 = "http://hm.baidu.com/hm.gif";

//    if (url.startWith(url1)) { return true; }
//    if (url.startWith(url2)) { return true; }
//    if (url.startWith(url3)) { return true; }
//    if (url.startWith(url4)) { return true; }
    if (url.startWith(url5)) { return true; }
    if (url.startWith(url6)) { return true; }

    return false;
};

page.onResourceRequested = function(requestData, request) {
    var url = requestData['url']

    console.log(url)

    if (_isImg2Ignore(url)) {
         console.log("--- " + url)
         request.abort()
         return
    }

    if (_isMatchedUrl(requestData.url)) {
        //console.log("requested: " + request.url);
        _pics[requestData.url] = true;
        console.log("+ " + requestData.url)
    }
};
page.onResourceReceived = function(response) {
    if (_isMatchedUrl(response.url) && 'end' == response.stage) {
        //console.log("received: " + response.url);
        if(_pics[response.url]){
            delete _pics[response.url];
            console.log("- " + response.url)
        }
    }
};

page.open(BOOK_URL, function(status) {
    console.log('starting... ');
    console.log('Fetch: ' + BOOK_URL);
    console.log('status: ' + status);

    if (status !== 'success') {
        console.log('Unable to access ' + BOOK_URL);
        phantom.exit(0);
    }else{
        //page.clearCookies();
        page.evaluate(function() {
            localStorage.clear();
        });
        _renderBook();
    }
});