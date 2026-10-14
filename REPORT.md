MSSV: 2A202602422

# Lab 11 · Scenario Forge — báo cáo

Thị trấn của tôi: B.

## 1. Phát lại log có trung thực không? (bước A)

Trong replay.json: 2/400 log bị bỏ vì người lái có va chạm; còn 398 log. Planner trên replay có 112 va chạm: 99 rear, 13 side, 0 front. Trong thế giới phản ứng có 0 va chạm; hai cách không có vụ nào chung.

99 vụ rear chủ yếu là va chạm giả do xe phía sau tiếp tục theo đúng chuyển động đã ghi của người lái, nên không phản ứng khi planner phanh ở thời điểm khác. Ví dụ replay_only scenario 0 là một va chạm rear; thế giới phản ứng có min TTC 7.53 s. Trong replay, xe bám đuôi không biết ego đã giảm tốc sớm hơn người lái trong log.

## 2. Kịch bản bất khả thi (bước B)

is_feasible loại kịch bản nếu gia tốc ngang khi chuyển làn (π/cutDur)² × 3.5/2 vượt mu×g; phanh sau nhập làn cutBrake vượt mu×g; người đi bộ chạy nhanh hơn 2.5 m/s; hoặc cutV không nằm trong (0, 22] m/s. Đây lần lượt là giới hạn ma sát lốp, lực phanh, tốc độ đi bộ và miền tốc độ hợp lý của xe.

hunt.json ghi số mẫu bị loại: bus_bypass 1, cut_in 4, crosswalk_block 5, rear_ended 21. Cuộc săn rear_ended bị kéo về nhiều kịch bản bất khả thi nhất vì chúng đạt điểm nguy hiểm cao; đếm chúng là va chạm sẽ thổi phồng xác suất bằng những tình huống không thể xảy ra ngoài đời.

## 3. Monte Carlo cho bạn biết gì (bước C1)

mc.json có 7 va chạm trong 3,000 lần chạy, p̂ = 0.002333; khoảng Wilson 95% là [0.001131, 0.004809]. Để sai số tương đối khoảng ±20%, xấp xỉ n ≈ 96/p, tức khoảng 41,143 lần chạy ở p̂ này.

Trong 3,000 lần chạy không thấy cut_in, crosswalk_block, rear_ended hay other. Không kết luận xác suất bằng 0: với k=0, cận trên Wilson 95% là 0.001279 cho mỗi nhóm.

## 4. Importance sampling, ESS và độ suy biến (bước C3)

estimate.json, mỗi kiểu và seed:

| Seed | Kiểu | p | Hits | ESS | top_share | Cận nếu 0 hit |
|---:|---|---:|---:|---:|---:|---:|
| 0 | bus_bypass | 1.659e-3 | 43 | 133.8 | 0.209 | — |
| 0 | cut_in | 0 | 0 | 126.4 | 0 | 2.5e-2 |
| 0 | crosswalk_block | 4.691e-7 | 90 | 135.0 | 0.149 | — |
| 0 | rear_ended | 0 | 0 | 137.1 | 0 | 2.5e-2 |
| 1 | bus_bypass | 1.178e-3 | 33 | 134.6 | 0.379 | — |
| 1 | cut_in | 0 | 0 | 108.6 | 0 | 2.5e-2 |
| 1 | crosswalk_block | 1.750e-7 | 71 | 148.0 | 0.275 | — |
| 1 | rear_ended | 0 | 0 | 108.0 | 0 | 2.5e-2 |
| 2 | bus_bypass | 3.453e-4 | 25 | 132.1 | 0.165 | — |
| 2 | cut_in | 0 | 0 | 118.0 | 0 | 2.5e-2 |
| 2 | crosswalk_block | 1.793e-6 | 95 | 116.2 | 0.688 | — |
| 2 | rear_ended | 0 | 0 | 111.1 | 0 | 2.5e-2 |

Các seed không đồng ý tốt: bus_bypass lệch gần 4.8 lần; crosswalk_block hơn 10 lần. Seed 2 của crosswalk_block có top_share 0.688, nghĩa là một mẫu nặng nhất mang gần 69% ước lượng. Những con số này còn nhiễu; hit count cao không sửa được đề xuất bị lệch. Với 0 hit, C3 báo cận 3/(0.2×600)=0.025, không báo 0.

other lấy từ Monte Carlo: estimate.json ghi k=0, n=3,000, cận trên 0.001279 (source mc.json). Không săn other vì đây là nhóm gom nhiều cơ chế không có một điểm nguy hiểm để xây đề xuất riêng. Ngân sách IS là 16,800 mẫu. Theo 96/p, Monte Carlo cần khoảng 41,143 mẫu ở p̂ của MC; ở trung vị tổng IS khoảng 1.179e-3 thì cần khoảng 81,400 mẫu để đạt ±20% tương đối. Ngân sách IS nhỏ hơn, nhưng ESS mỗi kiểu chỉ khoảng 108–148 và các seed cho thấy rủi ro bỏ sót.

## 5. Các kiểu thất bại (bước C2 + 3D)

hunt.json: cuộc săn bus_bypass tìm 126 lỗi bus_bypass; cuộc săn crosswalk_block tìm 54 lỗi crosswalk_block. Hai cuộc săn không tìm thấy lỗi cut_in hay rear_ended đúng kiểu mục tiêu; cuộc săn cut_in lại ghi 1 crosswalk_block và 27 bus_bypass, còn cuộc săn rear_ended ghi 15 crosswalk_block và 2 bus_bypass. Vì thế “không tìm thấy” chỉ là kết quả của ngân sách và điểm nguy hiểm hiện tại, không phải bằng chứng kiểu đó không tồn tại. Săn riêng từng kiểu giúp CEM không co hết về một kiểu dễ tìm.

Chuỗi bus_bypass: xe C2 lách qua xe buýt đang dừng rồi nhập lại ở tốc độ thấp, để ego va vào C2. Chuỗi crosswalk_block: người đi bộ bị xe buýt che khuất bắt đầu qua đường; ego phanh nhưng dừng với thân xe chắn lối trên vạch, khiến người đi bộ phải chờ.

evidence/viewer.json đã xuất 11 lượt xem và 6,000 điểm cloud. `evidence/shots/01-bus-bypass.png` và `02-crosswalk-block.png` lưu khung va chạm của hai kiểu tìm thấy; `03-crosswalk-block-current.png` lưu thêm khung chặn lối ở 20.5 s.

## 6. Sửa planner (bước E + 3D)

fix.json chọn policy {cutinLat: 2.6}. Trên TRAIN, policy này có fail=5.547e-6, fail_hi=1.479e-5, quãng đường 211.78 m và 8.05 khung phanh gấp; baseline lần lượt là 1.628e-3, 3.688e-3, 212.17 m và 8.00 khung.

Trên TEST mới, policy chọn có fail=1.469e-5, fail_hi_seen=3.273e-5, fail_hi hợp lệ=1.312e-3, quãng đường 215.43 m và 8.08 khung phanh gấp. Baseline TEST có fail=5.093e-4, fail_hi_seen=9.547e-4, fail_hi=2.234e-3, quãng đường 215.46 m và 8.23 khung. fail_hi của bản sửa lớn hơn fail điểm của baseline vì cận trên còn cộng khả năng có va chạm other chưa thấy: 0/3,000 lần chạy tự nhiên vẫn có cận Wilson 0.001279. Cận hợp lệ của bản sửa vẫn thấp hơn cận của baseline.

Một núm nghe có vẻ an toàn hơn không nhất thiết giảm mọi kiểu lỗi: tăng T từ 1.6 lên 2.0 giảm ước lượng bus_bypass trên TRAIN, nhưng crosswalk_block tăng từ 5.547e-6 lên 8.092e-6. Ước lượng theo kiểu còn nhiễu; đây là lý do phải nhìn cả các kiểu và TEST thay vì chỉ một con số. Các ảnh hiện có chưa gồm khung so sánh policy đã chọn với policy gốc dạng bóng mờ.

## 7. Từ mô phỏng ra đường thật

- cutGap: town B dùng median 12 m. Ước lượng gap nhận/khước từ các lần nhập làn trên quỹ đạo xe thực ở hành lang đô thị như dữ liệu FHWA Lankershim Boulevard. Nếu gap thực nhỏ hơn 12 m, xe nhập làn chấp nhận khe hẹp hơn và mô phỏng hiện tại có thể đánh giá thấp rủi ro; nếu lớn hơn, có thể đánh giá cao. [FHWA Lankershim Boulevard Dataset](https://www.fhwa.dot.gov/publications/research/operations/07029/)
- pedLook: town B giả định 85% người đi bộ nhìn qua xe buýt. Thay bằng video đồng bộ từ camera tại các điểm qua đường bị xe buýt che, do thành phố/đơn vị xe buýt thu thập và gán nhãn hướng nhìn, thời điểm bước xuống lề, và xe đang bị che hay nhìn thấy. Nếu tỷ lệ nhìn qua thực thấp hơn, mô phỏng đánh giá thấp người đi bộ bước ra bất ngờ và nguy cơ chặn vạch; nếu cao hơn, đánh giá cao. SHRP 2 NDS/RID là nguồn bổ sung cho hành vi lái, tuyến đường và điều kiện đường; dữ liệu cá nhân có quy trình cấp phép. [TRB SHRP 2 Safety Data Access](https://www.trb.org/StrategicHighwayResearchProgram2SHRP2/SHRP2DataSafetyAccess.aspx)
- wet/mu: town B giả định 30% đường ướt, với mu=0.5 khi ướt và 0.8 khi khô. Ghép nhật ký mưa/road-weather của tuyến với đo ma sát mặt đường liên tục và thông tin lốp. Nếu chuyến ướt hoặc ma sát thấp phổ biến hơn giả định, mô phỏng có thể đánh giá thấp va chạm do quãng phanh dài; nếu ít hơn, có thể đánh giá cao. FHWA mô tả thiết bị đo ma sát liên tục để lấy dữ liệu mạng đường. [FHWA Pavement Friction Primer](https://highways.fhwa.dot.gov/safety/rwd/keep-vehicles-road/pavement-friction/pavement-friction-road-safety-primer-friction)

## 8. Giới hạn

1. Đây chỉ là một con phố mô phỏng, một cấu hình xe buýt và một khoảng thời gian ngắn; không đại diện nút giao, nhiều làn, xe máy hay mọi kiểu đường.
2. Xe khác đi theo IDM và người đi bộ theo vài luật cố định; khác biệt tài xế, hành vi bất ngờ, giao tiếp mắt và lỗi cảm biến không được mô hình đầy đủ. Tầm nhìn chỉ bị che theo quy tắc xe buýt.
3. Phân phối latent là giả định dạy học, ít biến nhị phân và không khớp tương quan thật giữa thời tiết, mật độ xe, khe nhập làn và hành vi người đi bộ. Nếu có thêm một tuần, tôi sẽ thu thập video/trajectory đồng bộ ở nhiều tuyến, ước lượng các phân phối có điều kiện theo địa điểm và thời tiết, rồi kiểm định trên tuyến giữ lại.

## 9. Rắc rối của bạn (bước G + chương 10)

- Rắc rối là xe L1 phanh gấp khi ego đang bám cùng làn; tình huống tương ứng với xe dẫn đầu phanh khẩn cấp trong giao thông đô thị. Căn cứ không phải mọi lần phanh đều nguy hiểm: vấn đề là phanh mạnh trong khi xe sau có ít khoảng cách.
- hazard.json thay đổi h0_decel 6.0–7.5 m/s², h0_dur 1.2–3.0 s, h0_t0 0–1.5 s và h0_trig 24–42 m. exposure=0.05/chuyến là prior minh họa, không phải tỷ lệ đã đo. Ali (2023) báo cáo tài xế trung vị trong SHRP2 NDS có một sự kiện phanh 0.3g khoảng mỗi dặm trên đường khu dân cư tốc độ thấp; subset phanh mạnh khi bám gần cần được đo riêng bằng dữ liệu fleet địa phương. [Virginia Tech dissertation / SHRP2 NDS](https://vtechworks.lib.vt.edu/items/6bb2f65a-7a19-4a6d-a9e1-717ad5f5b5fb)
- mine.json: cảnh lưu sẵn không có va chạm; sweep giữ 1,036/1,500 mẫu khả thi (accepted=69%). Baseline có 3 va chạm ego: 0 avoidable, 0 unavoidable, 3 unattributed, 0 low_speed. Policy chọn có 0 ở cả bốn loại. P(lỗi planner | rắc rối)=0 trong mẫu, Wilson [0, 0.00369] cho cả hai. Nhân exposure: 0 điểm ước lượng/chuyến, cận trên 1.85e-4/chuyến. Đặt cạnh bus_bypass: trung vị IS theo seed là 1.179e-3; Monte Carlo cho 7/3,000 = 2.333e-3.
- avoidable là chuẩn lạc quan vì oracle phanh hết cỡ ngay khi thấy rắc rối, sớm hơn planner có thể phản ứng; phép thử chỉ dùng phanh nên cũng bỏ qua trường hợp đánh lái có thể tránh. Ba va chạm unattributed xảy ra trước khi hazard gây tác động, nên không phải bằng chứng lỗi do xe L1. File dùng ego=planner, không có lần tôi tự lái để so sánh.
- Kết quả hiện tại không cho thấy lỗi planner tránh được trong mẫu này. Nếu kiểm thử rộng hơn tìm thấy lỗi, bước tiếp theo là kiểm tra tăng khoảng cách theo thời gian T và thêm logic phanh khẩn cấp dựa trên deceleration dự đoán của xe dẫn đầu; cần đo trên TEST mới. Thư mục ảnh hiện có các khung chương 9 kể trên; chưa có ảnh riêng của rắc rối chương 10.
