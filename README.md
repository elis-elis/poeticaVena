# poeticaVena

**poeticaVena** is an online platform/website where users (poets) can explore, create, and collaborate on poetry within specific forms, such as Haiku and Free Verse. The platform combines modern web technologies and AI to offer real-time feedback, an interactive writing experience, and collaborative features. poeticaVena aims to engage poets in both creative writing and learning about various poetic forms, offering a space for practice and exploration.

## Key Features

- Creative Writing Tools: Users can write poems in specific forms (currently Haiku and Free Verse), with each form following unique structural guidelines.
- Real-Time Feedback: Provides feedback on syllable counts, rhyme matching (future development), and structure to help users adhere to poetic form requirements.
- Collaboration: Allows multiple users to contribute to a single poem, either in real-time or asynchronously, creating a shared writing experience.
- AI Assistance: Integrates OpenAI’s ChatGPT to offer creative feedback, structural suggestions, and interactive writing guidance.

![Screenshot-wireframe_poeticaVena.png](Screenshot-wireframe_poeticaVena.png)

## Technologies Used

- Backend
  - Framework: Flask, a lightweight Python framework for handling requests and API responses
  - Database: PostgreSQL, used to store user information, poems, collaborative writing sessions, and individual contributions
  - Authentication & Authorization: User sessions and permissions are managed securely using JWT (JSON Web Tokens), providing stateless and scalable user authentication.
- Additional Tools and APIs
  - ChatGPT API Integration: Provides users with AI-generated suggestions, feedback, and evaluations on syllable counts, structure, and rhyme matching (for future poetic forms).
  - Manual Syllable Counting Fallback: A custom function for syllable counting, offering a reliable alternative when AI feedback is not accessible.

## Project Scope and Current State

The platform is currently in its MVP (Minimum Viable Product) stage, focusing on the following functionalities:

- User Registration & Authentication: Users can sign up, log in, and securely manage their accounts.
- Poetry Editor: A simple interface for writing and editing poems, designed for Haiku and Free Verse formats. Future updates will add more poetic forms.
- Real-Time Feedback: Provides real-time syllable counting feedback and structure validation for Haiku. Future improvements will include rhyming feedback.
- AI Assistance: Integrates ChatGPT to give feedback on syllable counts and form adherence, supplemented by a manual syllable-counting function as a fallback.
- Collaboration & Version Control:
Users can invite collaborators to contribute to poems.
Every edit is stored as a version, so users can track the poem’s evolution over time with timestamps and editor details.

## Future Development Goals

- Additional Poetic Forms: Expand support to other types of poetry, such as Sestina, Acrostic, and Sonnet, with criteria-specific guidance.
- Advanced Feedback: Develop feedback for rhyme matching, grammar, tone, and theme analysis to enhance the AI’s creative support.
- Community Features: Enable users to rate, comment, and share poems with a community-driven space for poetry engagement.
- Mobile Optimization: Create a mobile-friendly interface or standalone mobile app for easier access on different devices.


## License

This project is licensed under the MIT License - see the LICENSE.md file for details.