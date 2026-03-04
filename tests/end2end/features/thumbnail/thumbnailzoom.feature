Feature: Zoom thumbnails.

    Background:
        Given I open any image
        And I enter thumbnail mode

    Scenario: Increase thumbnail size.
        When I run zoom in
        Then the thumbnail size should be 160

    Scenario: Decrease thumbnail size.
        When I run zoom out
        Then the thumbnail size should be 112

    Scenario: Increase thumbnail size multiple times.
        # 160
        When I run zoom in
        # 192
        And I run zoom in
        # 224
        And I run zoom in
        Then the thumbnail size should be 224

    Scenario: Try to decrease thumbnail size below limit.
        # 112
        When I run zoom out
        # 96
        And I run zoom out
        # 80
        And I run zoom out
        # 64
        And I run zoom out
        # 64
        And I run zoom out
        Then the thumbnail size should be 64
