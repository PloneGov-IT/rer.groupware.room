Changelog
=========

2.2.0 (unreleased)
------------------

- Add uninstall profile
  [cekk]

- If a user is removed from a group is also removed from the notification group. ticket #10347
  [arsenico13]

2.1.3 (2015-09-22)
------------------

- Speedup groupware_simple_groups_management.pt template
  [cekk]


2.1.2 (2014-02-03)
------------------

- Add "Owner" role to "Modify Portal content" permission in groupware_folders_workflow.
  Without this, normal contributors can't add Files and Images into Areas [cekk]


2.1.1 (2014-01-13)
------------------

- Added fixAreasOrder method to order alphabetically the areas after creation [cekk]
- Customized adapter for collective.blog.view to get results ordered by Date index [cekk]
- Renamed room's wf states. Now are published and private not open and closed [cekk]

2.1.0 (2013-11-05)
------------------

- Added custom simple_groups_management view that group groups by room [cekk]
- Added new field in control panel: allows to select wich collection type to use (old or new) [cekk]
- Removed unused modified_object and groups_event [cekk]
- Fixed DocumentsArea creation process. Now creates 2 collections [cekk]
- Group hosts are readers in the room [cekk]
- Added multi-language support in creation event [cekk]
- Added LocalManager to roles that can edit objects with folders_workflow [cekk]
- Added permissions from rer.groupware.security to room workflow [cekk]
- Coordinators can't add other users to coordinators group [cekk]

2.0.1 (2013-07-26)
------------------

- Added dependency to collective.blog.view [cekk]
- Added PlonePopoll to tiny linkable types [cekk]


2.0.0 (2013-06-24)
------------------

Plone 4 version

- z3c.autoinclude support [keul]
- Dependency on Popoll and Ploneboard [keul]
- Refactoring room setup config after creation [cekk]
- groupware_folders_workflow workflow moved there [keul]
- new open state [keul]
- Redefined getIconUrl method, that set room image as object icon, if given. [cekk]

1.3.2 (2013-04-17)
------------------

- Removed event that insert users in notify group when added in a room [cekk]


1.3.1 (2012-10-03)
------------------

- added revisor role to editorADV in forums [cekk]


1.3.0 (2012-10-01)
------------------

* added check field in room AT, for having a moderated forum [cekk]

1.2.1 (2012-03-12)
------------------

* Fixed Folders visualization in Area's collections [cekk]

1.2.0 (2012-03-12)
------------------

* Enabled adding Folders in Areas [cekk]

1.1.7 (2012-02-22)
------------------

* fixed topic criteria for DocumentsArea [cekk]

1.1.6 (2012-02-13)
------------------

* fixed topic criteria for DocumentsArea [cekk]

1.1.5 (2012-01-09)
------------------

* fixed labels (#335 & #349) [cekk]
* added BlogEntry to tiny linked items [cekk]

1.1.4 (2011-12-19)
------------------

* fixed mail text for rules and event when creating new items in a room [cekk]
* fixed created room event: now is fixed the default view for topics [cekk]
* added tiny configuration for room types [cekk]

1.1.3 (2011-07-08)
------------------

* Added image field for the room, and a viewlet that show the title of the room [cekk]
* Fixed accessibility of notification portlet with WAI ARIA roles [cekk]

1.1.2 (2011-04-22)
------------------

* fixed default attachment dimension for forums [cekk]

1.1.1 (2011-04-21)
------------------

* fixed sending email method [cekk]

1.1.0 (2011-04-05)
------------------

* removed reviewer role to editorAdv [cekk]
* customized notification methods: now creation and delete are managed by roles, and changes by an event [cekk]

1.0.7 (2011-01-26)
------------------

* fixed documents area topics [cekk]

1.0.6 (2011-01-26)
------------------

* fixed recursive topics [cekk]

1.0.5 (2011-01-25)
------------------

* fixed portlet name [cekk]

1.0.4 (2011-01-24)
------------------

* fixed portlet name [cekk]

1.0.3 (2011-01-20)
------------------

* fix event and group names [cekk]

1.0.2 (2011-01-17)
------------------

* Fix translation [cekk]

1.0.1 (2011-01-14)
------------------

* Fix creation method [cekk]
* fixed notification portlet [cekk]

1.0.0 (xxxx-xx-xx)
------------------

* Initial release
