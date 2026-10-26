# Comprehensive RAG Evaluation

## Bottom line

- Run: **Complete**; processed 10/10 cases.
- Expected-status matches: **10/10**.
- This is not a production readiness certificate or a universal accuracy score.
- If retrieval returns the entire corpus, high recall does not demonstrate selective retrieval quality.

### Findings requiring review

- **response-p1 / response_relevancy**: scored, 0.7731252263145879;
- **closure / factual_correctness**: scored, 0.67;
- **closure / response_relevancy**: scored, 0.8720247908362927;
- **closure / citation_support**: scored, 0.5;
- **recurring / factual_correctness**: scored, 0.67;
- **recurring / context_precision**: scored, 0.8055555555287036;
- **recurring / response_relevancy**: scored, 0.8235286137019577;
- **ticket-outage / context_precision**: scored, 0.49999999995;
- **ticket-outage / response_relevancy**: scored, 0.9415737012054644;
- **update-cadences / factual_correctness**: scored, 0.46;
- **update-cadences / context_precision**: scored, 0.0;
- **update-cadences / response_relevancy**: scored, 0.8332476021472859;
- **update-cadences / citation_support**: scored, 0.6;
- **security-after-hours / faithfulness**: scored, 0.8333333333333334;
- **security-after-hours / context_precision**: scored, 0.3333333333;
- **security-after-hours / response_relevancy**: scored, 0.6252598303909255;

## Metric summary

Higher is better for numeric scores; denominators differ by applicability.

| Metric | Mean | Scored | Skipped | Error/uncertain | Meaning |
| --- | ---: | ---: | ---: | ---: | --- |
| faithfulness | 0.983 | 10/10 | 0 | 0 | Support for factual statements in the retrieved context (all statuses). |
| factual_correctness | 0.800 | 6/10 | 4 | 0 | F1 agreement with the reference: supported facts and omissions. |
| context_precision | 0.606 | 6/10 | 4 | 0 | Whether relevant retrieved passages rank early. |
| context_recall | 1.000 | 6/10 | 4 | 0 | Coverage of reference facts by retrieved evidence. |
| response_relevancy | 0.811 | 6/10 | 4 | 0 | Question–answer alignment; not a truth score. |
| citation_coverage | 1.000 | 10/10 | 0 | 0 | Fraction of statements with nonempty, resolvable citation IDs. |
| citation_validity | 1.000 | 10/10 | 0 | 0 | Fraction of referenced IDs that exist in retrieved evidence. |
| citation_metadata | 1.000 | 10/10 | 0 | 0 | Resolved citation source/page matches trusted evidence. |
| citation_support | 0.910 | 10/10 | 0 | 0 | Judge support for statement–cited-passage pairs. |
| message_contract | 1.000 | 10/10 | 0 | 0 | No uncited SOP facts in the free-text message (custom rubric). |
| decision_quality | 1.000 | 10/10 | 0 | 0 | Appropriate answer, abstention or clarification (custom rubric). |

## Run provenance

- **input_path**: data\evaluation-english-prompt.json
- **input_sha256**: c346b01e8942ad0e60c36b79d36a994c74f952220a9d73b38b2d7ac14222ac43
- **judge_provider**: OMNIROUTE
- **judge_model**: cx/gpt-5.6-luna-low
- **ragas_version**: 0.4.3
- **rubric_version**: 1
- **generated_at**: 2026-10-26T08:27:01.897996+00:00
- **generation_provenance**: Unknown: historical input lacks generation metadata.
- **settings**: {'correctness_mode': 'f1', 'atomicity': 'low', 'coverage': 'low', 'relevancy_strictness': 3, 'faithfulness_scope': 'statements_only', 'embedding': 'google/embeddinggemma-300m', 'dimensions': 768, 'embedding_prompt_mode': 'query'}

## Per-case answers and evaluation

### response-p1

**Question:** Berapa target respons awal P1? Apakah masalah harus selesai dalam 15 menit?

**Status:** answered (expected: answered)

**Answer:**

- Target respons awal untuk tiket P1 adalah 15 menit. **[KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**
- Respons awal berarti petugas telah mengakui laporan dan menyampaikan langkah berikutnya; respons awal tidak berarti masalah harus sudah selesai dalam 15 menit. **[KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**

**Reference:** Target respons awal P1 adalah 15 menit. Respons awal berarti mengakui laporan dan menyampaikan langkah berikutnya, bukan masalah telah selesai.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | 1.0 (scored) |  |
| context_precision | 0.9999999999 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.7731252263145879 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The status is answered and the message is empty, satisfying the criterion. |
| decision_quality | pass (scored) | Respons menjawab kedua bagian pertanyaan secara langsung dan seluruh isinya didukung oleh referensi serta bukti: target respons awal P1 adalah 15 menit, tetapi penyelesaian masalah tidak diwajibkan dalam waktu tersebut. |
- Citation check, statement 1, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: pass. Passage explicitly states under “Target Respons Awal” that P1 has a target of 15 minutes.
- Citation check, statement 2, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: pass. Passage explicitly defines respons awal as acknowledging the report and communicating next steps, and states that it does not mean the problem is already solved; the 15-minute target applies only to P1 tickets.

### closure

**Question:** Kapan tiket boleh ditutup jika pelanggan tidak membalas, dan bagaimana pengecualian untuk P1?

**Status:** answered (expected: answered)

**Answer:**

- Tiket dapat ditutup setelah pelanggan mengonfirmasi penyelesaian atau setelah dua hari kerja tanpa tanggapan sejak notifikasi selesai. **[KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**
- Pengecualian untuk tiket P1 adalah tiket tersebut memerlukan konfirmasi eksplisit pelanggan sebelum ditutup, sehingga tidak dapat ditutup hanya karena dua hari kerja berlalu tanpa tanggapan. **[KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**

**Reference:** Tiket dapat ditutup setelah dua hari kerja tanpa tanggapan sejak notifikasi selesai. P1 memerlukan konfirmasi eksplisit pelanggan.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | 0.67 (scored) |  |
| context_precision | 0.9999999999 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.8720247908362927 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 0.5 (scored) |  |
| message_contract | pass (scored) | The status is answered and the message is empty, satisfying the criterion. |
| decision_quality | pass (scored) | Respons menjawab kedua bagian pertanyaan secara tepat dan sesuai dengan referensi serta bukti: penutupan setelah dua hari kerja tanpa tanggapan, dengan pengecualian P1 yang memerlukan konfirmasi eksplisit pelanggan. |
- Citation check, statement 1, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: fail. Fail: The passage includes an exception for P1 tickets, which require explicit customer confirmation, but the statement presents the two-day no-response rule without that exception.
- Citation check, statement 2, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: pass. Passage explicitly states that P1 tickets require explicit customer confirmation and are excluded from closure after two working days without a response.

### recurring

**Question:** Keluhan dengan isu sama terjadi lagi dalam 30 hari. Apakah otomatis P1?

**Status:** answered (expected: answered)

**Answer:**

- Tidak. Keluhan dengan isu yang sama dalam 30 hari ditandai sebagai keluhan berulang dan ditinjau oleh koordinator, tetapi tidak otomatis menjadi insiden P1; penentuan prioritas mengikuti dampak aktual. **[KB_02_Pengelolaan_Keluhan_Pelanggan.pdf, page 1]**

**Reference:** Keluhan ditandai berulang dan ditinjau koordinator. Tidak otomatis P1; prioritas mengikuti dampak aktual.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | 0.67 (scored) |  |
| context_precision | 0.8055555555287036 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.8235286137019577 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The status is answered and the message is empty, satisfying the criterion. |
| decision_quality | pass (scored) | Respons menjawab pertanyaan secara langsung dan sesuai dengan referensi serta bukti: keluhan berulang dalam 30 hari tidak otomatis menjadi P1, melainkan diprioritaskan berdasarkan dampak aktual. |
- Citation check, statement 1, `fbbd702f-0a1a-540c-96a9-632a5f3c3dec`: pass. Passage explicitly supports all substantive claims: same-issue complaints within 30 days are marked recurring and reviewed by the coordinator, are not automatically P1 incidents, and priority is based on actual impact.

### ticket-outage

**Question:** Apa yang dilakukan jika sistem tiket tidak tersedia dan setelah sistem pulih?

**Status:** answered (expected: answered)

**Answer:**

- Jika sistem tiket tidak tersedia, catat laporan dalam formulir sementara menggunakan waktu asli penerimaan. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**
- Setelah sistem pulih, masukkan kembali data laporan ke dalam sistem dan tandai bahwa tiket berasal dari pencatatan sementara. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**

**Reference:** Catat laporan dalam formulir sementara dengan waktu asli penerimaan. Setelah pulih, masukkan data kembali dan tandai berasal dari pencatatan sementara.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | 1.0 (scored) |  |
| context_precision | 0.49999999995 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.9415737012054644 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The message is empty, so it contains no factual SOP rules, numbers, deadlines, procedures, or exceptions. |
| decision_quality | pass (scored) | Respons menjawab kedua bagian pertanyaan secara langsung dan sesuai dengan referensi serta bukti: mencatat sementara dengan waktu asli, lalu memasukkan kembali data dan menandainya setelah sistem pulih. |
- Citation check, statement 1, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage explicitly supports recording reports in a temporary form when the ticketing system is unavailable and using the original receipt time.
- Citation check, statement 2, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage explicitly instructs re-entering the data after system recovery and marking the ticket as originating from temporary recording, supporting all substantive claims.

### update-cadences

**Question:** Jelaskan perbedaan jadwal pembaruan internal SEV1 dan pembaruan kepada pelanggan untuk tiket P1.

**Status:** answered (expected: answered)

**Answer:**

- Untuk insiden SEV1, pembaruan status internal dibuat setiap 20 menit. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1]**
- Untuk tiket P1, pembaruan kepada pelanggan diberikan setidaknya setiap 30 menit selama gangguan aktif. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**
- Komunikasi pelanggan pada SEV1 menggunakan ringkasan dampak, langkah mitigasi, dan waktu pembaruan berikutnya, tanpa mengungkap detail keamanan sensitif. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1]**
- SEV1 dan P1 adalah klasifikasi yang berbeda: SEV1 merupakan tingkat insiden, sedangkan P1 merupakan tingkat prioritas tiket; dokumen tidak menetapkan pemetaan otomatis antara keduanya. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1; KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**

**Reference:** Pembaruan internal SEV1 setiap 20 menit. Pembaruan pelanggan P1 setidaknya setiap 30 menit selama gangguan aktif. Keduanya berbeda audiens dan klasifikasi.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | 0.46 (scored) |  |
| context_precision | 0.0 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.8332476021472859 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 0.6 (scored) |  |
| message_contract | pass (scored) | The message is empty, so it contains no factual SOP rules, numbers, deadlines, procedures, or exceptions. |
| decision_quality | pass (scored) | Respons menjawab perbedaan jadwal dengan tepat: pembaruan internal SEV1 setiap 20 menit, sedangkan pembaruan pelanggan untuk P1 setidaknya setiap 30 menit selama gangguan aktif. Penjelasan audiens dan klasifikasi juga didukung oleh referensi. |
- Citation check, statement 1, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: pass. Passage explicitly states that for SEVI incidents, internal status updates are made every 20 minutes, directly supporting the statement.
- Citation check, statement 2, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage explicitly states that P1 tickets must be updated to customers at least every 30 minutes during an active disruption, matching the statement.
- Citation check, statement 3, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: pass. Passage explicitly states that for SEV1 customer communication uses an impact summary, mitigation steps, and the next update time without revealing sensitive security details.
- Citation check, statement 4, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: fail. Passage defines SEV1 as an incident level but does not mention P1, ticket priority, or any mapping between them, so it does not support all substantive claims.
- Citation check, statement 4, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: fail. Passage defines P1 as a ticket priority level but does not mention SEV1, nor does it establish that SEV1 is an incident level or that no automatic mapping exists. Therefore it does not support all substantive claims.

### ambiguous-update

**Question:** Untuk kasus kritis, saya harus memberi pembaruan setiap berapa menit?

**Status:** needs_clarification (expected: needs_clarification)

**Answer:**

- Jika yang dimaksud kasus kritis adalah tiket prioritas P1, pembaruan kepada pelanggan diberikan setidaknya setiap 30 menit selama gangguan aktif. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**
- Jika yang dimaksud adalah insiden SEV1, pembaruan status internal dibuat setiap 20 menit; dokumen tidak menetapkan interval waktu spesifik untuk pembaruan kepada pelanggan. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1]**

Apakah yang dimaksud kasus kritis adalah tiket P1 atau insiden SEV1?

**Reference:** Perlu klarifikasi apakah yang dimaksud pembaruan internal SEV1 atau pembaruan pelanggan P1. SEV1 internal setiap 20 menit; P1 pelanggan setidaknya setiap 30 menit selama gangguan aktif.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | None (skipped) | Not applicable or required factual input absent. |
| context_precision | None (skipped) | Not applicable or required factual input absent. |
| context_recall | None (skipped) | Not applicable or required factual input absent. |
| response_relevancy | None (skipped) | Not applicable or required factual input absent. |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The message is a question distinguishing interpretations, which is explicitly allowed, and the status is not answered. |
| decision_quality | pass (scored) | Pass: The response correctly identifies the ambiguity between P1 customer updates and SEV1 internal updates, accurately cites the intervals, notes the missing customer interval for SEV1, and asks a useful clarifying question. |
- Citation check, statement 1, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage states that P1 tickets are updated to customers at least every 30 minutes during an active outage, directly supporting the statement.
- Citation check, statement 2, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: pass. Passage explicitly states that for SEV1 internal status updates are made every 20 minutes. It describes customer communications and the next update but does not specify a fixed customer-update interval, supporting both claims.

### security-after-hours

**Question:** Ada dugaan paparan data sensitif di luar jam layanan. Kepada siapa dilaporkan dan bolehkah contoh data pribadi dimasukkan ke tiket umum?

**Status:** answered (expected: answered)

**Answer:**

- Dugaan paparan data sensitif diklasifikasikan sebagai SEV1 dan harus segera dilaporkan kepada koordinator insiden serta tim teknis piket, termasuk di luar jam layanan. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1]**
- Contoh data pribadi tidak boleh diunggah atau dimasukkan ke tiket umum. Indikasi kebocoran data harus segera dibatasi aksesnya dan dicatat melalui kanal keamanan. **[KB_04_Eskalasi_dan_Insiden.pdf, page 1]**

**Reference:** Dugaan paparan data sensitif termasuk SEV1. Segera laporkan kepada koordinator insiden dan tim teknis piket termasuk di luar jam layanan. Batasi akses, catat melalui kanal keamanan, dan jangan unggah contoh data pribadi ke tiket umum.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 0.8333333333333334 (scored) |  |
| factual_correctness | 1.0 (scored) |  |
| context_precision | 0.3333333333 (scored) |  |
| context_recall | 1.0 (scored) |  |
| response_relevancy | 0.6252598303909255 (scored) |  |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The status is answered and the message is empty, satisfying the criterion. |
| decision_quality | pass (scored) | Respons secara langsung menjawab kedua bagian pertanyaan dan sepenuhnya sesuai dengan referensi serta bukti: pelaporan kepada koordinator insiden dan tim teknis piket di luar jam layanan, serta larangan memasukkan contoh data pribadi ke tiket umum. |
- Citation check, statement 1, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: pass. Passage explicitly classifies suspected sensitive-data exposure as SEVI and requires immediate reporting to the incident coordinator and on-call technical team, including outside service hours.
- Citation check, statement 2, `62ca0e49-1cad-52b8-b9b8-8e87b492e16e`: pass. Passage explicitly states that personal data examples must not be uploaded to public tickets and that suspected data leaks must have access restricted immediately and be recorded through the security channel.

### refund-amount

**Question:** Berapa rupiah kompensasi pasti yang diterima pelanggan?

**Status:** unsupported (expected: unsupported)

**Answer:**

- Petugas tidak boleh menjanjikan pengembalian dana atau kompensasi sebelum ada persetujuan pejabat berwenang. **[KB_02_Pengelolaan_Keluhan_Pelanggan.pdf, page 1]**
- Setiap keputusan kompensasi harus dicatat bersama dasar persetujuannya. **[KB_02_Pengelolaan_Keluhan_Pelanggan.pdf, page 1]**

Informasi yang diminta tidak tersedia dalam dokumen yang diberikan.

**Reference:** Nominal kompensasi tidak disebutkan. Petugas tidak boleh menjanjikan kompensasi tanpa persetujuan pejabat berwenang.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | None (skipped) | Not applicable or required factual input absent. |
| context_precision | None (skipped) | Not applicable or required factual input absent. |
| context_recall | None (skipped) | Not applicable or required factual input absent. |
| response_relevancy | None (skipped) | Not applicable or required factual input absent. |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The message contains no SOP rules, numbers, deadlines, procedures, or exceptions; the status is unsupported, so the empty-message requirement for answered status does not apply. |
| decision_quality | pass (scored) | Respons tepat menyatakan bahwa nominal kompensasi tidak tersedia dan tidak mengarang jumlah, serta sesuai dengan referensi bahwa kompensasi memerlukan persetujuan pejabat berwenang. |
- Citation check, statement 1, `fbbd702f-0a1a-540c-96a9-632a5f3c3dec`: pass. Passage explicitly states that staff must not promise refunds or compensation before approval from an authorized official.
- Citation check, statement 2, `fbbd702f-0a1a-540c-96a9-632a5f3c3dec`: pass. Passage section 7 explicitly states that all compensation decisions must be recorded together with the basis for approval, directly supporting the statement.

### resolution-sla

**Question:** Berapa jam batas waktu penyelesaian masalah untuk tiket P2?

**Status:** unsupported (expected: unsupported)

**Answer:**

- Batas respons awal untuk tiket P2 adalah 1 jam; respons awal berarti pengakuan laporan dan penyampaian langkah berikutnya, bukan penyelesaian masalah. **[KB_01_Penanganan_Tiket_Layanan.pdf, page 1]**
- Jika tiket P2 belum selesai, pembaruan kepada pelanggan dilakukan setiap 4 jam kerja. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**

Informasi yang diminta tidak tersedia dalam dokumen yang diberikan.

**Reference:** SOP tidak menetapkan batas waktu penyelesaian P2. Target respons awal satu jam dan pembaruan empat jam kerja bukan batas penyelesaian.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | None (skipped) | Not applicable or required factual input absent. |
| context_precision | None (skipped) | Not applicable or required factual input absent. |
| context_recall | None (skipped) | Not applicable or required factual input absent. |
| response_relevancy | None (skipped) | Not applicable or required factual input absent. |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The message contains no factual SOP rules, numbers, deadlines, procedures, or exceptions; the empty-message requirement applies only when status is answered. |
| decision_quality | pass (scored) | Respons tepat menyatakan bahwa dokumen tidak menetapkan batas waktu penyelesaian P2 dan membedakannya dari target respons awal 1 jam serta pembaruan setiap 4 jam kerja. |
- Citation check, statement 1, `f71578e4-15ce-5064-9268-338b3ec7cc2e`: pass. Passage explicitly states that the P2 initial response target is 1 hour and defines initial response as acknowledging the report and communicating next steps, not resolving the problem.
- Citation check, statement 2, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage explicitly states that P2 tickets are updated every 4 working hours if not yet completed, supporting the entire statement.

### retention

**Question:** Berapa tahun tepatnya data pelanggan wajib disimpan?

**Status:** unsupported (expected: unsupported)

**Answer:**

- Dokumen hanya menyebutkan bahwa salinan lokal yang tidak lagi dibutuhkan harus dihapus sesuai kebijakan retensi, tetapi tidak mencantumkan durasi penyimpanan data pelanggan dalam tahun. **[KB_03_Panduan_Operasional_Layanan.pdf, page 1]**

Informasi yang diminta tidak tersedia dalam dokumen yang diberikan.

**Reference:** Durasi retensi tidak disebutkan dalam dokumen. SOP hanya merujuk kebijakan retensi untuk penghapusan salinan lokal yang tidak diperlukan.

| Metric | Score/verdict | Explanation |
| --- | --- | --- |
| faithfulness | 1.0 (scored) |  |
| factual_correctness | None (skipped) | Not applicable or required factual input absent. |
| context_precision | None (skipped) | Not applicable or required factual input absent. |
| context_recall | None (skipped) | Not applicable or required factual input absent. |
| response_relevancy | None (skipped) | Not applicable or required factual input absent. |
| citation_coverage | 1.0 (scored) |  |
| citation_validity | 1.0 (scored) |  |
| citation_metadata | 1.0 (scored) |  |
| citation_support | 1.0 (scored) |  |
| message_contract | pass (scored) | The message is an absence notice stating that the requested information is unavailable; it contains no SOP rules, numbers, deadlines, procedures, or exceptions. |
| decision_quality | pass (scored) | Respons dengan tepat menyatakan bahwa durasi penyimpanan dalam tahun tidak disebutkan dalam dokumen dan tidak mengarang informasi; ini sesuai dengan referensi dan bukti. |
- Citation check, statement 1, `e40bafb0-4f14-5a44-90c2-f0281562de6f`: pass. Passage states that local copies no longer needed must be deleted according to the retention policy, but it does not specify a customer data retention duration in years.

## How to draw a conclusion

- Low context recall: review missing evidence before changing the answer prompt.
- Low correctness with good grounding: inspect missing reference facts or exceptions.
- Low citation support: inspect the actual cited passage, not just retrieval as a whole.
- Decision/message failures: review abstention, clarification and uncited claims.
- Errors or uncertain judgments: fix or manually review them; do not count as zero.
- A small development set and a model judge do not establish generalization. Validate references and calibrate judgments with human review.
