import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.FileWriter;
import java.io.IOException;

import verifier.QAVerifierOneshot;

public class Main {
    public static void main(String[] args) {
        QAVerifierOneshot verifier = new QAVerifierOneshot();
        verifier.JSONMethod();
    }

}
