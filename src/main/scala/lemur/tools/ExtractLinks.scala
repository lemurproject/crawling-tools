package lemur.tools

import java.io.File
import java.util.regex.Pattern
import scala.Array.canBuildFrom
import scala.io.Source
import lemur.util.Warc
import net.htmlparser.jericho.StreamedSource
import scala.collection.JavaConversions._
import net.htmlparser.jericho.Tag
import java.io.Reader
import net.htmlparser.jericho.Config
import net.htmlparser.jericho.LoggerProvider
import java.io.InputStream

/**
 * Extracts links in pages stored in WARC files that match a regular expression.
 */
object ExtractLinks {

  def loadRegExps(path: File) = {
    val source = Source.fromFile(path)
    val patterns = source.getLines.filter(_.trim().length() > 0).map(Pattern.compile(_))

    patterns.toArray
  }

  def getLinks(data: InputStream): Option[List[String]] = {
    try {
      val source = new StreamedSource(data)

      val hrefs = for (
        segment <- source.iterator();
        if segment.isInstanceOf[Tag];
        val tag = segment.asInstanceOf[Tag];
        val attrs = tag.parseAttributes();
        if attrs != null;
        val href = attrs.getValue("href") if href != null
      ) yield href

      Some(hrefs.toList)
    } catch {
      case e: Exception => {
        None
      }
    }

  }

  def extractLinks(patterns: Array[Pattern], warcFile: File) = {
    val responses = for (
      rec <- Warc.readResponses(warcFile);
      (headers, body) = Warc.parseResponse(rec)
    ) yield body;

    val allLinks = responses.flatMap(getLinks)

    val links = allLinks.flatten.filter(link => {
      patterns.exists(_.matcher(link).matches())
    })

    links
  }

  def testFile(warcFile: File) = {
    printf("Testing file: %s\n", warcFile.toString())
    val responses = for (
      rec <- Warc.readResponses(warcFile);
      (headers, body) = Warc.parseResponse(rec)
    ) yield body;
    
    val allLinks = responses.flatMap(getLinks)
    
    var n = 0
    allLinks.foreach(items => {
      items.foreach(item => {
    	  n += 1        
      })
    })
    printf("Total links: %s\n", n)
  }
  
  def main(args: Array[String]) {
    if (args.length < 2) {
      println("Usage: ExtractLinks regexp-file file1.warc.gz ...");
      System.exit(1)
    }

    //Global settings
    Config.LoggerProvider = LoggerProvider.DISABLED

    val regexpFile = new File(args(0))
    val warcFiles = args.slice(1, args.length).map(new File(_))

    val patterns = loadRegExps(regexpFile)

    warcFiles.foreach(warcFile => {
      testFile(warcFile)
      //val links = extractLinks(patterns, warcFile)
      //links.foreach(println(_))
      
      
    })
  }
}