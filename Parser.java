import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.ling.TaggedWord;

public class Parser {
    public static void main(String[] args)
        throws FileNotFoundException, IOException {
        String filename = args[0];
        //String model = args[1];
        String model = "stanford-postagger/models/english-bidirectional-distsim.tagger";
        model = "stanford-postagger/models/english-left3words-distsim.tagger";
        File file = new File(filename);
        FileInputStream fis = new FileInputStream(file);
        byte[] data = new byte[(int) file.length()];
        fis.read(data);
        fis.close();

        MaxentTagger tagger = new MaxentTagger(model);

        String jsonData = new String(data, "UTF-8");
        JSONObject json = new JSONObject(jsonData);
        json.write(new FileWriter(new File(filename + ".tagged")));
        JSONArray chapters = json.getJSONArray("chapters");
        for (Object chapterObj : chapters) {
            JSONObject chapter = (JSONObject) chapterObj;
            JSONArray paragraphs = chapter.getJSONArray("paragraphs");
            for (Object paragraphObj : paragraphs) {
                JSONArray paragraph = (JSONArray) paragraphObj;
                for (Object chunkObj : paragraph) {
                    JSONObject chunk = (JSONObject) chunkObj;
                    String type = chunk.getString("type");
                    String chunkData = chunk.getString("data");
                    List<List<TaggedWord>> taggedSentences = tagger.process(
                        MaxentTagger.tokenizeText(new StringReader(chunkData)));

                    JSONArray sentences = new JSONArray();
                    for (List<TaggedWord> taggedSentence : taggedSentences) {
                        JSONArray sentence = new JSONArray();
                        for (TaggedWord word: taggedSentence) {
                            JSONObject info = new JSONObject();
                            info.put("word", word.word());
                            info.put("tag", word.tag());
                            sentence.put(info);
                        }
                        sentences.put(sentence);
                    }
                    chunk.put("sentences", sentences);
                }
            }
        }

        FileWriter output = new FileWriter(new File(filename + ".tagged"));
        json.write(output);
        output.close();
    }
}
