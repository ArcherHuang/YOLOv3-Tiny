gst-launch-1.0 \
rtspsrc location="rtsp://root:ubuntu168@169.254.11.31:554/live1s1.sdp" latency=1 \
! rtph264depay ! h264parse ! queue ! omxh264dec \
! queue ! tee name=t2 t2.src_0 ! queue \
! ivas_xmultisrc kconfig=/opt/xilinx/share/ivas/smartcam/yolov3tiny/preprocess.json ! queue \
! ivas_xfilter kernels-config=/opt/xilinx/share/ivas/smartcam/yolov3tiny/aiinference.json \
! ima2.sink_master ivas_xmetaaffixer name=ima2 ima2.src_master \
! fakesink t2.src_1 ! queue \
! ima2.sink_slave_0 ima2.src_slave_0 ! queue \
! ivas_xfilter kernels-config=/opt/xilinx/share/ivas/smartcam/yolov3tiny/drawresult.json ! queue \
! kmssink driver-name=xlnx plane-id=39 sync=false fullscreen-overlay=true