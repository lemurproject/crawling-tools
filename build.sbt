import AssemblyKeys._

name := "crawling-tools"

version := "0.1"


libraryDependencies += "net.htmlparser.jericho" % "jericho-html" % "3.1" withSources ()

libraryDependencies += "org.jwat" % "jwat-warc" % "0.9.1"  withSources ()

libraryDependencies += "org.apache.commons" % "commons-compress" % "1.4.1" withSources ()

libraryDependencies += "commons-io" % "commons-io" % "2.4"

// Enable sbt-assembly
assemblySettings

assembleArtifact in packageScala := true

