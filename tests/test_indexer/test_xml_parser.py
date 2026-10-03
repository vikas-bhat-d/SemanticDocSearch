from app.indexer.xml_parser import convert_backup_path, parse_incremental_xml


def test_convert_backup_path_pc135():
    input_path = r"E:\Winman Backup\Daily_INCREMENTAL(1)\Final-16-Jul-2015\PC135(D.)\Desktop\file.xlsx"
    expected = r"\\pc135\D\Desktop\file.xlsx"
    assert convert_backup_path(input_path) == expected


def test_convert_backup_path_server01():
    input_path = r"F:\Backups\SERVER01(C.)\Documents\report.pdf"
    expected = r"\\server01\C\Documents\report.pdf"
    assert convert_backup_path(input_path) == expected


def test_convert_backup_path_no_pattern():
    input_path = r"C:\Folder\subfolder\file.txt"
    assert convert_backup_path(input_path) == input_path


def test_parse_incremental_xml_content():
    xml_data = """<NewDataSet>
  <FILELIST>
    <Type>FOLDER</Type>
    <Value>E:\\Winman Backup\\Daily_INCREMENTAL(1)\\Final-16-Jul-2015\\PC135(D.)\\Desktop</Value>
  </FILELIST>
  <FILELIST>
    <Type>FILE</Type>
    <Value>E:\\Winman Backup\\Daily_INCREMENTAL(1)\\Final-16-Jul-2015\\PC135(D.)\\Desktop\\file.xlsx</Value>
  </FILELIST>
</NewDataSet>"""

    results = parse_incremental_xml(xml_data)
    assert len(results) == 2
    assert results[0] == ("FOLDER", r"\\pc135\D\Desktop")
    assert results[1] == ("FILE", r"\\pc135\D\Desktop\file.xlsx")
