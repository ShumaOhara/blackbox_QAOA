package verifier;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.FileWriter;
import java.io.IOException;


public class QAVerifierOneshot {
    private long[][] MakeTestColumns(){
        long[][] testColumns = {{1,2}, {3,4},{5,6}};
        return testColumns;
    }

    private int[][] MakeTestTable(){
        int[][] testTable = {{1,1,0}, {0, 1, 1}};
        return testTable;
    }

    private void convertJSON(long[][] Columns, int[][] Table){
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            String columns = objectMapper.writeValueAsString(Columns);
            FileWriter fileWriter1 = new FileWriter("json/columns.json");
            fileWriter1.write(columns);
            fileWriter1.close();
            System.out.println("Exported to Columns as a JSON file.");

            String table = objectMapper.writeValueAsString(Table);
            FileWriter fileWriter2 = new FileWriter("json/Table.json");
            fileWriter2.write(table);
            fileWriter2.close();
            System.out.println("Exported to Table as a JSON file.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void JSONMethod(){
        long[][] constraintColumns = MakeTestColumns();
        int[][] constraintTable = MakeTestTable();
        convertJSON(constraintColumns, constraintTable);
    }
}
