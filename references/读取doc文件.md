# 读取旧版 .doc 文件

python-docx 只支持 `.docx` 格式，不支持旧版 `.doc` 格式。

## 使用 olefile 读取 .doc

```bash
pip install olefile --break-system-packages
```

### 方法1：提取中文文本

```python
import olefile
import re

ole = olefile.OleFileIO('/path/to/file.doc')
word_stream = ole.openstream('WordDocument').read()

# 用 utf-16-le 解码
text = word_stream.decode('utf-16-le', errors='ignore')

# 提取中文字符
chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
result = ''.join(chinese_chars)
```

### 方法2：提取更完整的文本

```python
import olefile
import re

ole = olefile.OleFileIO('/path/to/file.doc')
word_stream = ole.openstream('WordDocument').read()

# 从偏移量 0x800 开始提取
text_start = 0x800
raw_bytes = word_stream[text_start:text_start+10000]

# utf-16-le 解码
text = raw_bytes.decode('utf-16-le', errors='ignore')

# 清理控制字符
text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
```

### 方法3：strings 命令（快速预览）

```bash
strings /path/to/file.doc | head -200
```

## 注意事项

- `.doc` 是 OLE2 复合文档格式，需要用 olefile 解析
- `utf-16-le` 是 Word 文档的内部编码
- 提取的文本可能包含乱码，需要进一步清理
- 对于格式化信息（标题、字体等），olefile 无法直接提取
- 如果需要完整格式信息，需要用 LibreOffice 转换为 `.docx`

## 其他工具

- `catdoc`：命令行工具，可提取 .doc 文本
- `antiword`：命令行工具，可提取 .doc 文本
- `mammoth`：Python库，但只支持 .docx
- LibreOffice：可将 .doc 转换为 .docx
