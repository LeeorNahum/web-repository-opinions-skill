# Open bug reports

## 412: Assistant says the image was added, board shows a broken image

I attached a photo in my chat assistant and asked it to put it on my "Garden" board. It said "Uploaded photo.jpg to Garden". The board shows a broken image. The tool call in the transcript was `upload_image { board_id: "Hq3k9TmPx2Ab", path: "/mnt/data/photo.jpg" }`.

## 418: Same thing from a coding agent

My coding agent generated a chart and called `upload_image` with `path: "sandbox:/workspace/out/chart.png"`. Success message, empty image on the board.

## 421: Feature request

Can the MCP tool take base64 so the assistant can paste the image straight in? A teammate tried and the assistant ran out of context on a 6 MB photo.
