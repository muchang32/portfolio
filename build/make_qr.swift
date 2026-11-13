import CoreImage
import Foundation

// 用系統內建的 CoreImage 產生 QR code，輸出成 SVG，再用 CIDetector 讀回來核對。
let args = CommandLine.arguments
let text = args[1], outPath = args[2]

let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(text.data(using: .utf8)!, forKey: "inputMessage")
filter.setValue("M", forKey: "inputCorrectionLevel")
let image = filter.outputImage!
let ctx = CIContext()
let ext = image.extent
let w = Int(ext.width), h = Int(ext.height)
var buf = [UInt8](repeating: 0, count: w * h * 4)
ctx.render(image, toBitmap: &buf, rowBytes: w * 4, bounds: ext,
           format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())

// CoreImage 自帶 1 格白邊，裁掉後由版面自己留白
var dark = [[Bool]]()
for y in 0..<h {
    var row = [Bool]()
    for x in 0..<w { row.append(buf[(y * w + x) * 4] < 128) }
    dark.append(row)
}
let xs = (0..<w).filter { x in (0..<h).contains { dark[$0][x] } }
let ys = (0..<h).filter { y in dark[y].contains(true) }
let x0 = xs.first!, x1 = xs.last!, y0 = ys.first!, y1 = ys.last!
let n = x1 - x0 + 1
var d = ""
for y in y0...y1 {
    var x = x0
    while x <= x1 {
        if dark[y][x] {
            var run = 1
            while x + run <= x1 && dark[y][x + run] { run += 1 }
            d += "M\(x - x0) \(y - y0)h\(run)v1h-\(run)z"
            x += run
        } else { x += 1 }
    }
}
let svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 \(n) \(y1 - y0 + 1)\" shape-rendering=\"crispEdges\"><path fill=\"#14110F\" d=\"\(d)\"/></svg>"
try! svg.write(toFile: outPath, atomically: true, encoding: .utf8)

// 讀回來核對內容
let big = image.transformed(by: CGAffineTransform(scaleX: 10, y: 10))
let det = CIDetector(ofType: CIDetectorTypeQRCode, context: ctx,
                     options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])!
let found = det.features(in: big).compactMap { ($0 as? CIQRCodeFeature)?.messageString }
print("modules=\(n) decoded=\(found)")
