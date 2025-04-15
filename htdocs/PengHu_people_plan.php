<?php
/**********************************************
 * 1. PHP 資料庫連線與撈取資料
 **********************************************/
$DB_HOST = '127.0.0.1';
$DB_USER = 'root';
$DB_PASS = 'nclab722';
$DB_NAME = 'penghu';

$query = "SELECT * FROM plan ORDER BY crowd_rank ASC";
$conn = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
if (!$conn) {
    die("連接失敗: " . mysqli_connect_error());
}

$number = array();
$place = array();
$latitude = array();
$longitude = array();
$crowdRank = array();

$result = mysqli_query($conn, $query);
if (!$result) {
    die("查詢錯誤: " . mysqli_error($conn));
}
while ($row = mysqli_fetch_array($result, MYSQLI_BOTH)) {
    $number[] = $row['no'];
    $place[] = $row['設置點'];
    $latitude[] = $row['緯度'];
    $longitude[] = $row['經度'];
    $crowdRank[] = $row['crowd_rank'];
}
mysqli_close($conn);

$userLat = isset($_GET['lat']) ? floatval($_GET['lat']) : null;
$userLng = isset($_GET['lng']) ? floatval($_GET['lng']) : null;
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>使用者路線規劃 - 澎湖行程規劃</title>
  <style>
    /* 全域與 RWD 版面設定 */
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background: #f9f9f9;
      color: #333;
    }
    h1 { text-align: center; margin: 10px 0; }
    #map { height: 60vh; width: 100%; background-color: #ccc; }
    #distanceInfo {
      position: relative;
      z-index: 10;
      background-color: rgba(255,255,255,0.9);
      padding: 8px;
      margin: 10px;
      text-align: center;
      font-size: 16px;
    }
    /* 按鈕容器 */
    #buttonPanel {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 8px;
      margin: 10px 0;
      padding: 0 10px;
    }
    #buttonPanel button {
      background-color: #4CAF50;
      border: none;
      color: white;
      padding: 10px 15px;
      font-size: 16px;
      cursor: pointer;
      border-radius: 5px;
      flex: 1 1 auto;
      max-width: 160px;
      min-width: 100px;
      text-align: center;
      transition: background-color 0.2s;
    }
    #buttonPanel button:hover { background-color: #45a049; }
    /* 下拉選單 */
    .dropdown {
      position: relative;
      display: inline-block;
      flex: 1 1 auto;
      max-width: 160px;
      min-width: 100px;
    }
    .dropbtn {
      width: 100%;
      background-color: #4CAF50;
      color: white;
      padding: 10px 15px;
      font-size: 16px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      text-align: center;
      transition: background-color 0.2s;
    }
    .dropbtn:hover { background-color: #45a049; }
    .dropdown-content {
      display: none;
      position: absolute;
      background-color: #fff;
      min-width: 100%;
      box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
      z-index: 999;
      border-radius: 5px;
      overflow: hidden;
    }
    .dropdown-content a {
      color: #333;
      padding: 10px 12px;
      text-decoration: none;
      display: block;
      font-size: 14px;
      border-bottom: 1px solid #eee;
    }
    .dropdown-content a:hover { background-color: #ddd; }
    @media screen and (max-width: 600px) {
      #buttonPanel { gap: 6px; }
      #buttonPanel button, .dropdown { max-width: 100%; flex: 1 1 100%; }
      #buttonPanel button { font-size: 14px; padding: 8px 10px; }
      .dropdown-content a { font-size: 14px; padding: 8px 10px; }
      #distanceInfo { font-size: 14px; margin: 10px 5px; padding: 10px; }
    }
    /* 使用者路線說明：固定在畫面下方並帶有水平捲軸 */
    #userRouteDesc {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(255,255,255,0.95);
      padding: 10px;
      font-size: 16px;
      text-align: center;
      z-index: 1000;
      white-space: nowrap;
      overflow-x: auto;
      max-width: 100%;
    }
  </style>
</head>
<body>
  <h1>使用者路線規劃</h1>
  <!-- 收起/展開控制面板 -->
  <div style="text-align:center; margin-bottom:10px;">
    <button onclick="togglePanel()">收起/展開控制面板</button>
  </div>
  <!-- 按鈕容器 -->
  <div id="buttonPanel">
    <button onclick="toggleAllMarkers()">顯示/隱藏景點</button>
    <button onclick="resetSelection()">重設選擇</button>
    <div class="dropdown">
      <button class="dropbtn">使用者路線</button>
      <div class="dropdown-content">
        <a href="#" onclick="planUserRoute()">一次性規劃</a>
        <a href="#" onclick="planUserStepByStepRoute()">分段規劃</a>
        <a href="#" onclick="planNextUserSegment()">下一步</a>
        <a href="#" onclick="clearUserRoute()">清除</a>
      </div>
    </div>
  </div>
  <!-- 預估時間資訊 -->
  <div id="distanceInfo"></div>
  <!-- 地圖容器 -->
  <div id="map"></div>
  <!-- 使用者路線說明（固定底部並帶有水平捲軸） -->
  <div id="userRouteDesc"></div>
  
  <script>
    // 先定義 getCrowdLabel 函式，確保後續能被呼叫
    function getCrowdLabel(rank, total) {
      var label = "";
      if (total === 1) {
        label = "<span style='color:green;'>低</span>";
      } else if (total === 2) {
        label = (rank == 1) ? "<span style='color:green;'>低</span>" : "<span style='color:red; font-weight:bold;'>高</span>";
      } else {
        if (rank <= total / 3) {
          label = "<span style='color:green;'>低</span>";
        } else if (rank <= (2 * total) / 3) {
          label = "<span style='color:orange;'>中</span>";
        } else {
          label = "<span style='color:red; font-weight:bold;'>高</span>";
        }
      }
      return label;
    }
    
    // 當頁面載入完成後，若螢幕寬度小於600px則預設隱藏控制面板
    document.addEventListener("DOMContentLoaded", function() {
      if(window.innerWidth < 600) {
        document.getElementById('buttonPanel').style.display = 'none';
      }
      var dropButtons = document.querySelectorAll(".dropbtn");
      dropButtons.forEach(function(btn) {
        btn.addEventListener("click", function(e) {
          var dropdownContent = this.nextElementSibling;
          if (dropdownContent.style.display === "block") {
            dropdownContent.style.display = "none";
          } else {
            document.querySelectorAll(".dropdown-content").forEach(function(content) {
              content.style.display = "none";
            });
            dropdownContent.style.display = "block";
          }
          e.stopPropagation();
        });
      });
      document.addEventListener("click", function() {
        document.querySelectorAll(".dropdown-content").forEach(function(content) {
          content.style.display = "none";
        });
      });
    });

    function togglePanel() {
      var panel = document.getElementById('buttonPanel');
      panel.style.display = (panel.style.display === 'none') ? 'flex' : 'none';
    }
    
    var map;
    var markers = [];
    var infoWindows = [];
    var showAllMarkers = true;
    var userMarker;
    var directionsService;
    var placesService;
    
    // 使用者路線相關變數
    // userRoute: 儲存選取的景點索引
    // userRouteCurrentLocation: 當前路段起點
    // userRouteStepIndex: 下一個規劃的目標景點索引（已到達的景點為 userRouteStepIndex - 1）
    var userRoute = [];
    var userRouteCurrentLocation;
    var userRouteStepIndex = 0;
    var userDrivingDuration = null;
    var userWalkingDuration = null;
    var userSegmentDistance = "";
    var userRouteRenderer = null;
    var userStepRenderer = null;
    
    // 從後端取得的資料
    var JS_number = <?php echo json_encode($number); ?>;
    var JS_place = <?php echo json_encode($place); ?>;
    var JS_latitude = <?php echo json_encode($latitude); ?>;
    var JS_longitude = <?php echo json_encode($longitude); ?>;
    var JS_crowdRank = <?php echo json_encode($crowdRank); ?>;
    
    var userLat = <?php echo $userLat ? $userLat : 'null'; ?>;
    var userLng = <?php echo $userLng ? $userLng : 'null'; ?>;
    
    var totalCount = <?php echo count($number); ?>;
    console.log("總共景點數量：" + totalCount);
    
    // 更新使用者路線清單：
    // 若 i == userRouteStepIndex - 1：顯示綠色（已到達）
    // 若 i < userRouteStepIndex - 1：灰色（之前的）
    // 其他：原色
    // 更新後自動捲動到綠色元素
    function updateUserRouteList() {
      var listHTML = "【使用者路線】 ";
      for (var i = 0; i < userRoute.length; i++) {
        if (userRouteStepIndex > 0 && i == userRouteStepIndex - 1) {
          listHTML += "<span class='current' style='color: green; font-weight: bold;'>" + JS_place[userRoute[i]] + "</span>";
        } else if (userRouteStepIndex > 1 && i < userRouteStepIndex - 1) {
          listHTML += "<span style='color: gray;'>" + JS_place[userRoute[i]] + "</span>";
        } else {
          listHTML += JS_place[userRoute[i]];
        }
        if (i < userRoute.length - 1) {
          listHTML += " → ";
        }
      }
      var routeDesc = document.getElementById("userRouteDesc");
      routeDesc.innerHTML = listHTML;
      
      // 自動捲動到綠色（current）元素
      var currentElem = routeDesc.querySelector(".current");
      if (currentElem) {
        currentElem.scrollIntoView({ behavior: "smooth", inline: "center" });
      }
    }
    
    function initMap() {
      directionsService = new google.maps.DirectionsService();
      var center = (userLat && userLng) ? {lat: userLat, lng: userLng} : {lat: 23.57226, lng: 119.57102};
      map = new google.maps.Map(document.getElementById('map'), { center: center, zoom: 12 });
      placesService = new google.maps.places.PlacesService(map);
      
      if (userLat && userLng) {
        userMarker = new google.maps.Marker({
          position: {lat: userLat, lng: userLng},
          map: map,
          icon: {
            url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
            scaledSize: new google.maps.Size(32,32),
            origin: new google.maps.Point(0,0),
            anchor: new google.maps.Point(16,32)
          },
          title: "您的位置"
        });
      }
      for (var i = 0; i < JS_number.length; i++) {
        createMarker(i);
      }
      console.log("標記數量：" + markers.length);
    }
    
    function createMarker(i) {
      var pos = new google.maps.LatLng(parseFloat(JS_latitude[i]), parseFloat(JS_longitude[i]));
      var rank = JS_crowdRank[i];
      var crowdLabel = getCrowdLabel(rank, totalCount);
      
      var marker = new google.maps.Marker({
        position: pos,
        map: map,
        icon: {
          url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          scaledSize: new google.maps.Size(32,32),
          origin: new google.maps.Point(0,0),
          anchor: new google.maps.Point(16,32)
        },
        opacity: 0.8,
        title: JS_place[i] + " (人潮：" + crowdLabel + ")"
      });
      marker.addListener('click', function() { getPlaceDetails(marker, JS_place[i], i); });
      markers.push(marker);
    }
    
    function getPlaceDetails(marker, placeName, index) {
      var req = { query: placeName, fields: ['place_id'] };
      placesService.findPlaceFromQuery(req, function(results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK && results && results.length > 0) {
          var detailsReq = { placeId: results[0].place_id, fields: ['name', 'formatted_address', 'photos', 'opening_hours', 'rating'] };
          placesService.getDetails(detailsReq, function(place, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
              var content = "<h3>" + place.name + "</h3>";
              if (place.photos && place.photos.length > 0) {
                var photoUrl = place.photos[0].getUrl({maxWidth: 200});
                content = "<img src='" + photoUrl + "' style='width:200px;height:auto;border:1px solid #ccc;margin-bottom:5px;'><br>" + content;
              }
              content += "<p>" + (place.formatted_address || "") + "</p>";
              if (place.opening_hours) {
                content += "<p><strong>營業時間：</strong><br>" + place.opening_hours.weekday_text.join("<br>") + "</p>";
              }
              if (place.rating) {
                content += "<p><strong>評分：</strong>" + place.rating + "</p>";
              }
              var rank = JS_crowdRank[index];
              var crowdLabel = getCrowdLabel(rank, totalCount);
              content += "<p><strong>人潮：</strong>" + crowdLabel + "</p>";
              // 加入路線按鈕
              content += "<button onclick='addToUserRoute(" + index + ")'>加入路線</button>";
              var infoWin = new google.maps.InfoWindow({ content: content });
              closeAllInfoWindows();
              infoWin.open(map, marker);
              infoWindows.push(infoWin);
            } else { 
              alert("無法取得詳細資訊: " + status); 
            }
          });
        } else { 
          alert("查無相關景點資訊: " + status); 
        }
      });
    }
    
    function closeAllInfoWindows() {
      for (var i = 0; i < infoWindows.length; i++) {
        infoWindows[i].close();
      }
      infoWindows = [];
    }
    
    function toggleAllMarkers() {
      showAllMarkers = !showAllMarkers;
      for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(showAllMarkers ? map : null);
      }
      if (!showAllMarkers) { closeAllInfoWindows(); }
    }
    
    // 使用者路線相關函式
    function resetSelection() {
      userRoute = [];
      updateUserRouteList();
      if (userRouteRenderer) userRouteRenderer.setMap(null);
      if (userStepRenderer) userStepRenderer.setMap(null);
      document.getElementById("distanceInfo").innerHTML = "";
      // 恢復所有標記圖示為紅色
      for (var i = 0; i < markers.length; i++) {
        markers[i].setIcon({
          url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          scaledSize: new google.maps.Size(32,32),
          origin: new google.maps.Point(0,0),
          anchor: new google.maps.Point(16,32)
        });
      }
    }
    
    function addToUserRoute(index) {
      if (userRoute.indexOf(index) === -1) {
        userRoute.push(index);
        updateUserRouteList();
        // 將該 marker 變更為綠色，表示已加入路線
        markers[index].setIcon({
          url: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
          scaledSize: new google.maps.Size(32,32),
          origin: new google.maps.Point(0,0),
          anchor: new google.maps.Point(16,32)
        });
        // 顯示提示：已加入路線，2秒後關閉
        var info = new google.maps.InfoWindow({ content: "已加入路線" });
        info.open(map, markers[index]);
        setTimeout(function(){ info.close(); }, 2000);
      } else { 
        alert("此景點已加入規劃路線！"); 
      }
    }
    
    function planUserRoute() {
      if (userRoute.length < 1) {
        alert("請至少選擇1個景點來規劃路線！");
        return;
      }
      if (userStepRenderer) { userStepRenderer.setMap(null); }
      var origin = (userLat && userLng) ? {lat: userLat, lng: userLng} : markers[userRoute[0]].getPosition();
      var destination = markers[userRoute[userRoute.length - 1]].getPosition();
      var waypoints = [];
      for (var i = 0; i < userRoute.length; i++) {
        waypoints.push({ location: markers[userRoute[i]].getPosition(), stopover: true });
      }
      waypoints.pop();
      if (userRouteRenderer) { userRouteRenderer.setMap(null); }
      userRouteRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: false,
        polylineOptions: { strokeColor: '#008000' }
      });
      userRouteRenderer.setMap(map);
      directionsService.route({
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        travelMode: google.maps.TravelMode.DRIVING
      }, function(response, status) {
        if (status === 'OK') {
          userRouteRenderer.setDirections(response);
        } else {
          alert("無法規劃使用者整體路線: " + status);
        }
      });
    }
    
    // 分段規劃邏輯：
    // 1. 若有定位資訊，按「分段規劃」時，初始規劃為【使用者位置 → 第一個景點】，
    //    完成後將第一個景點視為已到達（綠色），並將 userRouteStepIndex 設為 1。
    // 2. 若無定位，則以【第一個景點】作為起點，直接將 userRouteStepIndex 設為 1，更新清單顯示第一個景點為綠色。
    function planUserStepByStepRoute() {
      if (userRoute.length < 1) {
        alert("請至少選擇1個景點來規劃路線！");
        return;
      }
      if (userRouteRenderer) { userRouteRenderer.setMap(null); }
      document.getElementById("distanceInfo").innerHTML = "";
      userDrivingDuration = null;
      userWalkingDuration = null;
      userSegmentDistance = "";
      
      if (userLat && userLng) {
        // 有定位資訊：以使用者位置為起點，規劃【使用者 → 第一個景點】
        userRouteCurrentLocation = {lat: userLat, lng: userLng};
        directionsService.route({
          origin: userRouteCurrentLocation,
          destination: markers[userRoute[0]].getPosition(),
          travelMode: google.maps.TravelMode.DRIVING
        }, function(response, status) {
          if (status === 'OK') {
            userStepRenderer = new google.maps.DirectionsRenderer({
              suppressMarkers: true,
              preserveViewport: true,
              polylineOptions: { strokeColor: '#FFA500' }
            });
            userStepRenderer.setMap(map);
            userStepRenderer.setDirections(response);
            userDrivingDuration = response.routes[0].legs[0].duration.value;
            userSegmentDistance = response.routes[0].legs[0].distance.text;
            // 更新起點為第一個景點
            userRouteCurrentLocation = markers[userRoute[0]].getPosition();
            // 設定 userRouteStepIndex 為 1，表示第一個景點已到達（綠色顯示）
            userRouteStepIndex = 1;
            updateUserSegmentInfo();
            updateUserRouteList();
          } else {
            alert("無法規劃使用者路線駕車段: " + status);
          }
        });
        directionsService.route({
          origin: userRouteCurrentLocation,
          destination: markers[userRoute[0]].getPosition(),
          travelMode: google.maps.TravelMode.WALKING
        }, function(response, status) {
          if (status === 'OK') {
            userWalkingDuration = response.routes[0].legs[0].duration.value;
            updateUserSegmentInfo();
          } else {
            alert("無法規劃使用者路線步行段: " + status);
          }
        });
      } else {
        // 無定位資訊：直接以第一個景點作為起點，並標示為已到達
        userRouteCurrentLocation = markers[userRoute[0]].getPosition();
        userRouteStepIndex = 1;
        updateUserRouteList();
      }
    }
    
    // 每按一次「下一步」，規劃從目前起點到下一個景點的路線
    function planNextUserSegment() {
      if (userRouteStepIndex >= userRoute.length) {
        alert("已完成所有使用者路線規劃！");
        return;
      }
      var segOrigin = userRouteCurrentLocation;
      var segDestination = markers[userRoute[userRouteStepIndex]].getPosition();
      if (userStepRenderer) { userStepRenderer.setMap(null); }
      userStepRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        preserveViewport: true,
        polylineOptions: { strokeColor: '#FFA500' }
      });
      userStepRenderer.setMap(map);
      directionsService.route({
        origin: segOrigin,
        destination: segDestination,
        travelMode: google.maps.TravelMode.DRIVING
      }, function(response, status) {
        if (status === 'OK') {
          userStepRenderer.setDirections(response);
          userDrivingDuration = response.routes[0].legs[0].duration.value;
          userSegmentDistance = response.routes[0].legs[0].distance.text;
          // 更新起點：到達此段目的地後，將此景點視為已到達
          userRouteCurrentLocation = segDestination;
          userRouteStepIndex++;
          updateUserSegmentInfo();
          updateUserRouteList();
        } else {
          alert("無法規劃使用者路線駕車段: " + status);
        }
      });
      directionsService.route({
        origin: segOrigin,
        destination: segDestination,
        travelMode: google.maps.TravelMode.WALKING
      }, function(response, status) {
        if (status === 'OK') {
          userWalkingDuration = response.routes[0].legs[0].duration.value;
          updateUserSegmentInfo();
        } else {
          alert("無法規劃使用者路線步行段: " + status);
        }
      });
    }
    
    function updateUserSegmentInfo() {
      if (userDrivingDuration !== null && userWalkingDuration !== null) {
        var moto = Math.round(userDrivingDuration * 0.8);
        document.getElementById("distanceInfo").innerHTML =
          "本段距離：" + userSegmentDistance +
          "，步行：" + formatDuration(userWalkingDuration) +
          "，騎摩托：" + formatDuration(moto) +
          "，開車：" + formatDuration(userDrivingDuration);
        userDrivingDuration = null;
        userWalkingDuration = null;
      }
    }
    
    function formatDuration(sec) {
      var minutes = Math.floor(sec / 60);
      var s = Math.round(sec % 60);
      return minutes > 0 ? minutes + " 分 " + s + " 秒" : s + " 秒";
    }
    
    // 將 clearUserRoute 函式掛到全域
    function clearUserRoute() {
      userRoute = [];
      updateUserRouteList();
      if (userRouteRenderer) userRouteRenderer.setMap(null);
      if (userStepRenderer) userStepRenderer.setMap(null);
      document.getElementById("distanceInfo").innerHTML = "";
      for (var i = 0; i < markers.length; i++) {
        markers[i].setIcon({
          url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          scaledSize: new google.maps.Size(32,32),
          origin: new google.maps.Point(0,0),
          anchor: new google.maps.Point(16,32)
        });
      }
    }
    window.clearUserRoute = clearUserRoute;
    
  </script>
  <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBkBeV2pKxDvLzQmcCe1X6jkqWMFhVXiuI&libraries=places&callback=initMap" async defer></script>
</body>
</html>
