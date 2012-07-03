Keyteq deploy tool
==================

Simple deployment of sites from dev to stage | production.

Simply navigate to the root folder of your sites extension and do

`fab stage` or `fab deploy`

In order for this to work you need to enhance your `extension.xml` (You _do_ know about this file already right?) with a few lines:
This example is for **http://ezexceed.com**

```xml
<software>
    <deploy>
        <site>ezexceed</site>
        <extension>ezexceed-site</extension>
    </deploy>

    <!-- The rest of the normal extension.xml -->
</software>
```

In addition to setting deploy targets you are able to more specific target dependencies
on top of the normal eZ Publish extension.xml options by setting a few attributes pr `<extension>`:
Once again this is from **http://ezexceed.com**

```xml
    <dependencies>
        <requires>
            <extension name="ezexceed" branch="develop" repo="https://github.com/KeyteqLabs/ezexceed.git" />
        </requires>
    </dependencies>
```

So using the two new attributes `branch` and `repo` we can automate initial clone, and update to `HEAD` of a given branch.
If no `branch` and `repo` is given, it will simply attempt a `git pull`
