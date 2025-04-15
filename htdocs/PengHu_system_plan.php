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

// 取得使用者位置（可從 GET 傳入）
$userLat = isset($_GET['lat']) ? floatval($_GET['lat']) : null;
$userLng = isset($_GET['lng']) ? floatval($_GET['lng']) : null;
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>系統路線規劃 - 澎湖行程規劃</title>
  <style>
    /* 全域與 RWD 版面配置 */
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 0;
      font-family: Arial, sans-serif;
      background: #f9f9f9; color: #333;
    }
    h1 { text-align: center; margin: 10px 0; }
    #map { height: 60vh; width: 100%; background-color: #ccc; }
    #distanceInfo {
      position: relative; z-index: 10;
      background-color: rgba(255,255,255,0.9);
      padding: 8px; margin: 10px;
      text-align: center; font-size: 16px;
    }
    /* 控制面板 */
    #buttonPanel {
      display: flex; flex-wrap: wrap; justify-content: center;
      gap: 8px; margin: 10px 0; padding: 0 10px;
    }
    #buttonPanel button {
      background-color: #4CAF50; border: none; color: white;
      padding: 10px 15px; font-size: 16px; cursor: pointer;
      border-radius: 5px; flex: 1 1 auto;
      max-width: 160px; min-width: 100px;
      text-align: center; transition: background-color 0.2s;
    }
    #buttonPanel button:hover { background-color: #45a049; }
    .dropdown {
      position: relative; display: inline-block; flex: 1 1 auto;
      max-width: 160px; min-width: 100px;
    }
    .dropbtn {
      width: 100%; background-color: #4CAF50; color: white;
      padding: 10px 15px; font-size: 16px; border: none;
      border-radius: 5px; cursor: pointer; text-align: center;
      transition: background-color 0.2s;
    }
    .dropbtn:hover { background-color: #45a049; }
    .dropdown-content {
      display: none; position: absolute;
      background-color: #fff; min-width: 100%;
      box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
      z-index: 999; border-radius: 5px; overflow: hidden;
    }
    .dropdown-content a {
      color: #333; padding: 10px 12px; text-decoration: none;
      display: block; font-size: 14px; border-bottom: 1px solid #eee;
    }
    .dropdown-content a:hover { background-color: #ddd; }
    @media screen and (max-width: 600px) {
      #buttonPanel { gap: 6px; }
      #buttonPanel button, .dropdown { max-width: 100%; flex: 1 1 100%; }
      #buttonPanel button { font-size: 14px; padding: 8px 10px; }
      .dropdown-content a { font-size: 14px; padding: 8px 10px; }
      #distanceInfo { font-size: 14px; margin: 10px 5px; padding: 10px; }
    }
    /* 系統路線說明：依據分段進度動態更新，並自動捲動到下一站 */
    #systemRouteDesc {
      text-align: center;
      font-size: 16px;
      margin: 10px;
      white-space: nowrap;
      overflow-x: auto;
      max-width: 100%;
    }
  </style>
</head>
<body>
  <h1>系統路線規劃</h1>
  <!-- 收起/展開控制面板 -->
  <div style="text-align:center; margin-bottom:10px;">
    <button onclick="togglePanel()">收起/展開控制面板</button>
  </div>
  <!-- 控制面板 -->
  <div id="buttonPanel">
    <button onclick="toggleAllMarkers()">顯示/隱藏景點</button>
    <div class="dropdown">
      <button class="dropbtn">系統路線</button>
      <div class="dropdown-content">
        <a href="#" onclick="planEntireSystemRoute(); return false;">整段規劃</a>
        <a href="#" onclick="planStepByStepRoute(); return false;">分段規劃</a>
        <a href="#" onclick="planNextSegment(); return false;">下一步</a>
        <a href="#" onclick="clearSystemRoute(); return false;">清除系統路線</a>
      </div>
    </div>
  </div>
  <!-- 預估時間資訊 -->
  <div id="distanceInfo"></div>
  <!-- 地圖容器 -->
  <div id="map"></div>
  <!-- 系統路線說明：依據分段進度動態更新 -->
  <div id="systemRouteDesc"></div>
  
  <script>
    // 將全域函式掛在 window 上，方便下拉選單調用
    window.planEntireSystemRoute = planEntireSystemRoute;
    window.planStepByStepRoute = planStepByStepRoute;
    window.planNextSegment = planNextSegment;
    window.clearSystemRoute = clearSystemRoute;
    
    function togglePanel() {
      var panel = document.getElementById('buttonPanel');
      panel.style.display = (panel.style.display === 'none') ? 'flex' : 'none';
    }
    
    var map, markers = [], infoWindows = [], showAllMarkers = true;
    var directionsService, placesService;
    var initialRouteRenderer = null, stepByStepRenderer = null;
    var currentLocation = null, currentStepIndex = 0, drivingDuration = null, walkingDuration = null, segmentDistance = "";
    
    var totalCount = <?php echo count($number); ?>;
    console.log("總共景點數量：" + totalCount);
    
    var JS_number = <?php echo json_encode($number); ?>;
    var JS_place = <?php echo json_encode($place); ?>;
    var JS_latitude = <?php echo json_encode($latitude); ?>;
    var JS_longitude = <?php echo json_encode($longitude); ?>;
    var JS_crowdRank = <?php echo json_encode($crowdRank); ?>;
    var userLat = <?php echo $userLat ? $userLat : 'null'; ?>;
    var userLng = <?php echo $userLng ? $userLng : 'null'; ?>;
    
    // 更新系統路線說明函式
    // 依據 currentStepIndex 更新說明，並自動捲動到下一站的位置
    function updateSystemRouteDesc() {
      var descHTML = "【系統路線】 ";
      for (var i = 0; i < markers.length; i++) {
        if (i < currentStepIndex) {
          descHTML += "<span style='color: gray;'>" + JS_place[i] + "</span>";
        } else if (i === currentStepIndex) {
          descHTML += "<span id='nextStation' style='color: green; font-weight: bold;'>" + JS_place[i] + " (下一站)</span>";
        } else {
          descHTML += JS_place[i];
        }
        if (i < markers.length - 1) { descHTML += " → "; }
      }
      var descElem = document.getElementById("systemRouteDesc");
      descElem.innerHTML = descHTML;
      // 自動捲動到下一站
      var next = document.getElementById("nextStation");
      if (next) {
        next.scrollIntoView({behavior: "smooth", inline: "center", block: "nearest"});
      }
    }
    
    function getCrowdLabel(rank, total) {
      var label = "";
      if (total === 1) { label = "<span style='color:green;'>低</span>"; }
      else if (total === 2) { label = (rank == 1) ? "<span style='color:green;'>低</span>" : "<span style='color:red; font-weight:bold;'>高</span>"; }
      else {
        if (rank <= total / 3) { label = "<span style='color:green;'>低</span>"; }
        else if (rank <= (2 * total) / 3) { label = "<span style='color:orange;'>中</span>"; }
        else { label = "<span style='color:red; font-weight:bold;'>高</span>"; }
      }
      return label;
    }
    
    function initMap() {
      directionsService = new google.maps.DirectionsService();
      var center = (userLat && userLng) ? {lat: userLat, lng: userLng} : {lat: 23.57226, lng: 119.57102};
      map = new google.maps.Map(document.getElementById('map'), { center: center, zoom: 12 });
      placesService = new google.maps.places.PlacesService(map);
      
      if (userLat && userLng) {
        new google.maps.Marker({
          position: {lat: userLat, lng: userLng},
          map: map,
          icon: { url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png", scaledSize: new google.maps.Size(32,32), origin: new google.maps.Point(0,0), anchor: new google.maps.Point(16,32) },
          title: "您的位置"
        });
      }
      for (var i = 0; i < JS_number.length; i++) { createMarker(i); }
      console.log("標記數量：" + markers.length);
      updateSystemRouteDesc();
    }
    
    function createMarker(i) {
      var pos = new google.maps.LatLng(parseFloat(JS_latitude[i]), parseFloat(JS_longitude[i]));
      var rank = JS_crowdRank[i];
      var crowdLabel = getCrowdLabel(rank, totalCount);
      
      var marker = new google.maps.Marker({
        position: pos,
        map: map,
        icon: { url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png", scaledSize: new google.maps.Size(32,32), origin: new google.maps.Point(0,0), anchor: new google.maps.Point(16,32) },
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
              // 系統路線頁面不需要加入路線按鈕
              var infoWin = new google.maps.InfoWindow({ content: content });
              closeAllInfoWindows();
              infoWin.open(map, marker);
              infoWindows.push(infoWin);
            } else { alert("無法取得詳細資訊: " + status); }
          });
        } else { alert("查無相關景點資訊: " + status); }
      });
    }
    
    function closeAllInfoWindows() {
      for (var i = 0; i < infoWindows.length; i++) { infoWindows[i].close(); }
      infoWindows = [];
    }
    
    function toggleAllMarkers() {
      showAllMarkers = !showAllMarkers;
      for (var i = 0; i < markers.length; i++) { markers[i].setMap(showAllMarkers ? map : null); }
      if (!showAllMarkers) { closeAllInfoWindows(); }
    }
    
    // 系統路線：整段規劃（紅線）
    function planInitialRoute() {
      var total = markers.length;
      if (total === 0) return;
      var hasUserPos = (userLat && userLng);
      var origin, destination, waypoints = [];
      if (hasUserPos) {
        origin = {lat: userLat, lng: userLng};
        destination = markers[total - 1].getPosition();
        for (var i = 0; i < total - 1; i++) {
          waypoints.push({ location: markers[i].getPosition(), stopover: true });
        }
      } else {
        origin = markers[0].getPosition();
        destination = markers[total - 1].getPosition();
        for (var i = 1; i < total - 1; i++) {
          waypoints.push({ location: markers[i].getPosition(), stopover: true });
        }
      }
      if (initialRouteRenderer) { initialRouteRenderer.setMap(null); }
      initialRouteRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        preserveViewport: true,
        polylineOptions: { strokeColor: '#FF0000' }
      });
      initialRouteRenderer.setMap(map);
      directionsService.route({
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        travelMode: google.maps.TravelMode.DRIVING,
        provideRouteAlternatives: true,
        optimizeWaypoints: true,
        drivingOptions: {
          departureTime: new Date(),
          trafficModel: google.maps.TrafficModel.BEST_GUESS
        }
      }, function(response, status) {
        if (status === 'OK') {
          initialRouteRenderer.setDirections(response);
          // 完整規劃完成後，將 currentStepIndex 設為總數，表示全部完成
          currentStepIndex = total;
          updateSystemRouteDesc();
        } else { alert("無法規劃自動路線: " + status); }
      });
    }
    
    function planEntireSystemRoute() { 
      if (stepByStepRenderer) { stepByStepRenderer.setMap(null); } 
      planInitialRoute(); 
    }
    
    function clearSystemRoute() { 
      if (initialRouteRenderer) { initialRouteRenderer.setMap(null); }
      if (stepByStepRenderer) { stepByStepRenderer.setMap(null); }
      document.getElementById("distanceInfo").innerHTML = "";
      currentStepIndex = 0;
      updateSystemRouteDesc();
    }
    
    // 系統路線：分段規劃（藍線）
    function planStepByStepRoute() {
      if (initialRouteRenderer) { initialRouteRenderer.setMap(null); }
      if (userLat && userLng) {
        currentLocation = {lat: userLat, lng: userLng};
        currentStepIndex = 0;
      } else {
        if (markers.length > 0) {
          currentLocation = markers[0].getPosition();
          currentStepIndex = 1;
        } else { alert("沒有景點資料可供規劃"); return; }
      }
      if (stepByStepRenderer) { stepByStepRenderer.setMap(null); }
      document.getElementById("distanceInfo").innerHTML = "";
      planNextSegment();
    }
    
    function planNextSegment() {
      console.log("planNextSegment triggered, currentStepIndex: " + currentStepIndex);
      if (currentStepIndex >= markers.length) { 
        alert("系統路線規劃完成！");
        return;
      }
      var segOrigin = currentLocation;
      var segDestination = markers[currentStepIndex].getPosition();
      if (stepByStepRenderer) { stepByStepRenderer.setMap(null); }
      stepByStepRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        preserveViewport: true,
        polylineOptions: { strokeColor: '#0000FF' }
      });
      stepByStepRenderer.setMap(map);
      directionsService.route({
        origin: segOrigin,
        destination: segDestination,
        travelMode: google.maps.TravelMode.DRIVING,
        drivingOptions: {
          departureTime: new Date(),
          trafficModel: google.maps.TrafficModel.BEST_GUESS
        }
      }, function(response, status) {
        if (status === 'OK') {
          stepByStepRenderer.setDirections(response);
          drivingDuration = response.routes[0].legs[0].duration.value;
          segmentDistance = response.routes[0].legs[0].distance.text;
          currentLocation = segDestination;
          // 先更新說明，然後再將 currentStepIndex 增加
          updateSegmentInfo();
          updateSystemRouteDesc();
          currentStepIndex++;
        } else { alert("無法規劃系統駕車路線: " + status); }
      });
      directionsService.route({
        origin: segOrigin,
        destination: segDestination,
        travelMode: google.maps.TravelMode.WALKING
      }, function(response, status) {
        if (status === 'OK') { 
          walkingDuration = response.routes[0].legs[0].duration.value; 
          updateSegmentInfo(); 
        } else { alert("無法規劃系統步行路線: " + status); }
      });
    }
    
    function updateSegmentInfo() {
      if (drivingDuration !== null && walkingDuration !== null) {
        var motoDuration = Math.round(drivingDuration * 0.8);
        document.getElementById("distanceInfo").innerHTML =
          "系統路線本段距離：" + segmentDistance +
          "，預計耗時：步行：" + formatDuration(walkingDuration) +
          "，騎摩托：" + formatDuration(motoDuration) +
          "，開車：" + formatDuration(drivingDuration);
        drivingDuration = null;
        walkingDuration = null;
      }
    }
    
    function formatDuration(sec) {
      var minutes = Math.floor(sec / 60);
      var s = Math.round(sec % 60);
      return minutes > 0 ? minutes + " 分 " + s + " 秒" : s + " 秒";
    }
    
    document.addEventListener("DOMContentLoaded", function() {
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
  </script>
  <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBkBeV2pKxDvLzQmcCe1X6jkqWMFhVXiuI&libraries=places&callback=initMap" async defer></script>
</body>
</html>
